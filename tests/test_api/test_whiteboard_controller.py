"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import json
from random import randint
from uuid import uuid4

from flask import current_app as app
from squiggy import std_commit
from squiggy.api.whiteboard_socket_handler import join_whiteboard
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import is_teaching
from squiggy.models.course import Course
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession
from tests.util import mock_s3_bucket, override_config

unauthorized_user_id = '666'


def _api_get_whiteboard(whiteboard_id, client, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetWhiteboard:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_owner_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        fake_auth.login(mock_whiteboard['users'][0]['id'])
        asset = _api_get_whiteboard(client=client, whiteboard_id=mock_whiteboard['id'])
        assert asset['id'] == mock_whiteboard['id']

    def test_teacher_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        course = Course.find_by_id(mock_whiteboard['courseId'])
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard['id'], client=client)
        assert asset['id'] == mock_whiteboard['id']


class TestGetWhiteboards:

    @classmethod
    def _api_get_whiteboards(
            cls,
            client,
            expected_status_code=200,
            include_deleted=False,
            limit=None,
            offset=None,
            order_by=None,
    ):
        params = {
            'includeDeleted': include_deleted,
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
        }
        response = client.post(
            '/api/whiteboards',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_whiteboards(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_whiteboards(client, expected_status_code=401)

    def test_false_feature_flag(self, authorized_user_id, client, fake_auth, mock_whiteboard):
        """Denies authorized user when feature flag is false."""
        with override_config(app, 'FEATURE_FLAG_WHITEBOARDS', False):
            fake_auth.login(authorized_user_id)
            self._api_get_whiteboards(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Get all whiteboards."""
        course, student, whiteboard = _create_student_whiteboard()
        assert student.id in [user['id'] for user in whiteboard['users']]

        # Deleted whiteboard
        deleted_whiteboard = Whiteboard.create(
            course_id=course.id,
            title='Deleted',
            users=[student],
        )
        Whiteboard.delete(deleted_whiteboard['id'])
        std_commit(allow_test_environment=True)

        for user in [
            _get_sample_user(canvas_course_role='Administrator', course=course),
            student,
            _get_sample_user(canvas_course_role='Teacher', course=course),
        ]:
            assert user
            fake_auth.login(user.id)
            # Simulate a visit to /whiteboard page
            join_whiteboard(
                current_user=LoginSession(user.id),
                socket_id=str(randint(1, 9999999)),
                whiteboard_id=whiteboard['id'],
            )
            std_commit(allow_test_environment=True)

            api_json = self._api_get_whiteboards(
                client=client,
                include_deleted=True,
                order_by='collaborator',
            )
            whiteboards = api_json['results']
            assert len(whiteboards) == api_json['total']

            whiteboard_sessions = WhiteboardSession.find(whiteboard['id'])
            my_whiteboard_session = next((s for s in whiteboard_sessions if s.user_id == user.id), None)
            if user.canvas_course_role == 'Student':
                assert my_whiteboard_session
            else:
                assert not my_whiteboard_session

            whiteboards_deleted = next((w for w in whiteboards if w['deletedAt']), [])
            if user.canvas_course_role == 'Administrator':
                assert len(whiteboards_deleted)
            else:
                assert len(whiteboards_deleted) == 0


class TestExportAsAsset:

    @staticmethod
    def _api_export(
            client,
            title,
            whiteboard_id,
            category_ids=(),
            description=None,
            expected_status_code=200,
    ):
        params = {
            'categoryIds': category_ids,
            'description': description,
            'title': title,
        }
        response = client.post(
            f'/api/whiteboard/{whiteboard_id}/export/asset',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        self._api_export(
            client,
            expected_status_code=401,
            title='Asset of anonymous user',
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_export(
            client,
            expected_status_code=401,
            title='Asset of an unauthorized user',
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_authorized(self, client, fake_auth):
        """Authorized user can export whiteboard as asset."""
        course, student, whiteboard = _create_student_whiteboard()
        fake_auth.login(student.id)
        WhiteboardElement.create(
            element={
                'fontSize': 14,
                'uuid': str(uuid4()),
            },
            whiteboard_id=whiteboard['id'])
        std_commit(allow_test_environment=True)
        with mock_s3_bucket(app):
            api_json = self._api_export(
                client,
                title='A is for Asset.',
                whiteboard_id=whiteboard['id'],
            )
            assert 'id' in api_json


class TestRestoreWhiteboard:

    @staticmethod
    def _api_restore_whiteboard(client, whiteboard_id, expected_status_code=200):
        response = client.get(f'/api/whiteboard/{whiteboard_id}/restore')
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        self._api_restore_whiteboard(client, whiteboard_id=mock_whiteboard['id'], expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_restore_whiteboard(client, whiteboard_id=mock_whiteboard['id'], expected_status_code=401)

    def test_authorized(self, authorized_user_id, client, fake_auth, mock_whiteboard):
        """Authorized user can update whiteboard."""
        fake_auth.login(authorized_user_id)
        Whiteboard.delete(mock_whiteboard['id'])
        std_commit(allow_test_environment=True)
        api_json = self._api_restore_whiteboard(client, whiteboard_id=mock_whiteboard['id'])
        assert api_json['deletedAt'] is None
        assert client.get(f"/api/whiteboard/{mock_whiteboard['id']}").json['deletedAt'] is None


# class TestRefreshAssetPreview:
#     """Refresh asset preview API."""
#
#     @staticmethod
#     def _api_refresh_whiteboard_preview(whiteboard_id, client, expected_status_code=200):
#         response = client.post(f'/api/whiteboard/{whiteboard_id}/refresh_preview')
#         assert response.status_code == expected_status_code
#
#     def test_anonymous(self, client, mock_whiteboard):
#         """Denies anonymous user."""
#         self._api_refresh_whiteboard_preview(mock_whiteboard['id'], client, expected_status_code=401)
#
#     def test_unauthorized(self, client, fake_auth, mock_whiteboard):
#         """Denies unauthorized user."""
#         fake_auth.login(unauthorized_user_id)
#         self._api_refresh_whiteboard_preview(mock_whiteboard['id'], client, expected_status_code=401)
#
#     def test_refresh_whiteboard_by_owner(self, client, db_session, fake_auth, mock_whiteboard):
#         """Authorized user can refresh asset preview."""
#         mock_whiteboard.preview_status = 'done'
#         fake_auth.login(mock_whiteboard.users[0].id)
#         asset_feed = _api_get_whiteboard(mock_whiteboard['id'], client)
#         assert asset_feed['previewStatus'] == 'done'
#         self._api_refresh_whiteboard_preview(mock_whiteboard['id'], client)
#         asset_feed = _api_get_whiteboard(mock_whiteboard['id'], client)
#         assert asset_feed['previewStatus'] == 'pending'
#
#     def test_refresh_whiteboard_by_instructor(self, client, db_session, fake_auth, mock_whiteboard):
#         """Instructor can refresh asset preview."""
#         mock_whiteboard.preview_status = 'done'
#         course = Course.find_by_id(mock_whiteboard['courseId'])
#         instructors = list(filter(lambda u: is_teaching(u), course.users))
#         fake_auth.login(instructors[0].id)
#         asset_feed = _api_get_whiteboard(mock_whiteboard['id'], client)
#         assert asset_feed['previewStatus'] == 'done'
#         self._api_refresh_whiteboard_preview(mock_whiteboard['id'], client)
#         asset_feed = _api_get_whiteboard(mock_whiteboard['id'], client)
#         assert asset_feed['previewStatus'] == 'pending'
#
#
# class TestDeleteWhiteboard:
#     """Delete whiteboard API."""
#
#     @staticmethod
#     def _api_delete_whiteboard(whiteboard_id, client, expected_status_code=200):
#         response = client.delete(f'/api/whiteboard/{whiteboard_id}/delete')
#         assert response.status_code == expected_status_code
#
#     def test_anonymous(self, client):
#         """Denies anonymous user."""
#         self._api_delete_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)
#
#     def test_unauthorized(self, client, fake_auth):
#         """Denies unauthorized user."""
#         fake_auth.login(unauthorized_user_id)
#         self._api_delete_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)
#
#     def test_delete_whiteboard_by_teacher(self, client, fake_auth, mock_whiteboard):
#         """Authorized user can delete whiteboard."""
#         course = Course.find_by_id(mock_whiteboard['courseId'])
#         instructors = list(filter(lambda u: is_teaching(u), course.users))
#         fake_auth.login(instructors[0].id)
#         self._verify_delete_whiteboard(mock_whiteboard['id'], client)
#
#     def _verify_delete_whiteboard(self, whiteboard_id, client):
#         self._api_delete_whiteboard(whiteboard_id=whiteboard_id, client=client)
#         std_commit(allow_test_environment=True)
#         response = client.get(f'/api/whiteboard/{whiteboard_id}')
#         assert response.status_code == 404

def _create_student_whiteboard():
    course = Course.find_by_canvas_course_id(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=1502870,
    )
    student = User.create(
        canvas_course_role='Student',
        canvas_enrollment_state='active',
        canvas_full_name='Born to Collaborate',
        canvas_user_id=987654321,
        course_id=course.id,
    )
    whiteboard = Whiteboard.create(
        course_id=course.id,
        title='CyberCulture',
        users=[student],
    )
    return course, student, whiteboard


def _get_sample_user(canvas_course_role, course):
    return next((u for u in course.users if u.canvas_course_role == canvas_course_role), None)
