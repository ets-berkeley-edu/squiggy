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
import random

from squiggy import std_commit
from squiggy.lib.util import is_teaching
from squiggy.models.course import Course
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession

unauthorized_user_id = '666'


def _api_get_whiteboard(whiteboard_id, client, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetWhiteboard:
    """Whiteboard API."""

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        _api_get_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_owner_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        fake_auth.login(mock_whiteboard.users[0].id)
        asset = _api_get_whiteboard(client=client, whiteboard_id=mock_whiteboard.id)
        assert asset['id'] == mock_whiteboard.id

    def test_teacher_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        course = Course.find_by_id(mock_whiteboard.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard.id, client=client)
        assert asset['id'] == mock_whiteboard.id


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

    def test_authorized(self, authorized_user_id, client, fake_auth, mock_whiteboard):
        """Get all whiteboards."""
        user = User.find_by_id(authorized_user_id)
        # Include deleted
        deleted_title = 'Delete me'
        whiteboard = Whiteboard.create(
            course_id=mock_whiteboard.course_id,
            title=deleted_title,
            users=[user],
        )
        Whiteboard.delete(whiteboard.id)
        # Session
        WhiteboardSession.upsert(
            socket_id=str('%032x' % random.getrandbits(128)),
            user_id=user.id,
            whiteboard_id=mock_whiteboard.id,
        )
        std_commit(allow_test_environment=True)
        # Test
        fake_auth.login(user.id)
        api_json = self._api_get_whiteboards(client=client, include_deleted=True)
        whiteboards = api_json['results']
        assert len(whiteboards) == api_json['total']
        assert next((w for w in whiteboards if w['deletedAt']), None)
        whiteboard_with_session = next((w for w in whiteboards if len(w['sessions'])), None)
        assert len(whiteboard_with_session['sessions']) == 1


class TestExportAsAsset:

    @staticmethod
    def _api_export(
            client,
            whiteboard_id,
            category_ids=[],
            description=None,
            title=None,
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
        self._api_export(client, whiteboard_id=mock_whiteboard.id, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_export(client, whiteboard_id=mock_whiteboard.id, expected_status_code=401)

    def test_authorized(self, authorized_user_id, client, fake_auth, mock_whiteboard):
        """Authorized user can export whiteboard as asset."""
        fake_auth.login(authorized_user_id)
        WhiteboardElement.create(
            element={},
            uid='765432',
            whiteboard_id=mock_whiteboard.id,
        )
        std_commit(allow_test_environment=True)
        api_json = self._api_export(client, whiteboard_id=mock_whiteboard.id)
        assert 'id' in api_json


# class TestUpdateWhiteboard:
#     """Update whiteboard API."""
#
#     @staticmethod
#     def _api_update_whiteboard(client, asset, expected_status_code=200):
#         params = {
#             'assetId': whiteboard.id,
#             'categoryId': whiteboard.categories[0].id if len(asset.categories) else None,
#             'description': whiteboard.description,
#             'title': whiteboard.title,
#         }
#         response = client.post(
#             '/api/whiteboard/update',
#             data=json.dumps(params),
#             content_type='application/json',
#         )
#         assert response.status_code == expected_status_code
#         return json.loads(response.data)
#
#     def test_anonymous(self, client, mock_whiteboard):
#         """Denies anonymous user."""
#         self._api_update_whiteboard(client, asset=mock_whiteboard, expected_status_code=401)
#
#     def test_unauthorized(self, client, fake_auth, mock_whiteboard):
#         """Denies unauthorized user."""
#         fake_auth.login(unauthorized_user_id)
#         self._api_update_whiteboard(client, asset=mock_whiteboard, expected_status_code=401)
#
#     def test_update_whiteboard_by_owner(self, client, fake_auth, mock_whiteboard):
#         """Authorized user can update whiteboard."""
#         fake_auth.login(mock_whiteboard.users[0].id)
#         self._verify_update_whiteboard(client, mock_whiteboard)
#
#     def test_update_whiteboard_by_teacher(self, client, fake_auth, mock_whiteboard):
#         """Authorized user can update whiteboard."""
#         course = Course.find_by_id(mock_whiteboard.course_id)
#         instructors = list(filter(lambda u: is_teaching(u), course.users))
#         fake_auth.login(instructors[0].id)
#         self._verify_update_whiteboard(client, mock_whiteboard)
#
#     def _verify_update_whiteboard(self, client, mock_whiteboard):
#         mock_whiteboard.title = "I'll be your mirror"
#         mock_whiteboard.description = "Reflect what you are, in case you don't know"
#         mock_whiteboard.categories = [mock_category]
#         api_json = self._api_update_whiteboard(client, asset=mock_whiteboard)
#         assert api_json['id'] == mock_whiteboard.id
#         assert len(api_json['categories']) == 1
#         assert api_json['categories'][0]['id'] == mock_category.id
#         assert api_json['description'] == mock_whiteboard.description
#         assert api_json['title'] == mock_whiteboard.title
#
#
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
#         self._api_refresh_whiteboard_preview(mock_whiteboard.id, client, expected_status_code=401)
#
#     def test_unauthorized(self, client, fake_auth, mock_whiteboard):
#         """Denies unauthorized user."""
#         fake_auth.login(unauthorized_user_id)
#         self._api_refresh_whiteboard_preview(mock_whiteboard.id, client, expected_status_code=401)
#
#     def test_refresh_whiteboard_by_owner(self, client, db_session, fake_auth, mock_whiteboard):
#         """Authorized user can refresh asset preview."""
#         mock_whiteboard.preview_status = 'done'
#         fake_auth.login(mock_whiteboard.users[0].id)
#         asset_feed = _api_get_whiteboard(mock_whiteboard.id, client)
#         assert asset_feed['previewStatus'] == 'done'
#         self._api_refresh_whiteboard_preview(mock_whiteboard.id, client)
#         asset_feed = _api_get_whiteboard(mock_whiteboard.id, client)
#         assert asset_feed['previewStatus'] == 'pending'
#
#     def test_refresh_whiteboard_by_instructor(self, client, db_session, fake_auth, mock_whiteboard):
#         """Instructor can refresh asset preview."""
#         mock_whiteboard.preview_status = 'done'
#         course = Course.find_by_id(mock_whiteboard.course_id)
#         instructors = list(filter(lambda u: is_teaching(u), course.users))
#         fake_auth.login(instructors[0].id)
#         asset_feed = _api_get_whiteboard(mock_whiteboard.id, client)
#         assert asset_feed['previewStatus'] == 'done'
#         self._api_refresh_whiteboard_preview(mock_whiteboard.id, client)
#         asset_feed = _api_get_whiteboard(mock_whiteboard.id, client)
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
#         course = Course.find_by_id(mock_whiteboard.course_id)
#         instructors = list(filter(lambda u: is_teaching(u), course.users))
#         fake_auth.login(instructors[0].id)
#         self._verify_delete_whiteboard(mock_whiteboard.id, client)
#
#     def _verify_delete_whiteboard(self, whiteboard_id, client):
#         self._api_delete_whiteboard(whiteboard_id=whiteboard_id, client=client)
#         std_commit(allow_test_environment=True)
#         response = client.get(f'/api/whiteboard/{whiteboard_id}')
#         assert response.status_code == 404
