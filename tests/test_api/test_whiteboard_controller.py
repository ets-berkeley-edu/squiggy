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

from itertools import groupby
import json
from random import randint
from uuid import uuid4

from flask import current_app as app
from flask_login import logout_user
from squiggy import db, std_commit
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import is_admin, is_teaching
from squiggy.models.activity import Activity
from squiggy.models.course import Course
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession
from tests.util import mock_s3_bucket

unauthorized_user_id = '666'


def _api_get_whiteboard(client, whiteboard_id, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetWhiteboard:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_whiteboard(client=client, expected_status_code=401, whiteboard_id=1)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_whiteboard(client=client, expected_status_code=401, whiteboard_id=1)

    def test_deleted_whiteboard(self, client, fake_auth):
        """Students cannot reach deleted whiteboards."""
        course, student, whiteboard = _create_student_whiteboard()
        whiteboard_id = whiteboard['id']
        Whiteboard.delete(whiteboard_id)
        std_commit(allow_test_environment=True)

        fake_auth.login(student.id)
        assert Whiteboard.find_by_id(LoginSession(student.id), whiteboard_id)['deletedAt']
        _api_get_whiteboard(client, expected_status_code=404, whiteboard_id=whiteboard_id)

    def test_owner_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        fake_auth.login(mock_whiteboard['users'][0]['id'])
        asset = _api_get_whiteboard(client=client, whiteboard_id=mock_whiteboard['id'])
        assert asset['id'] == mock_whiteboard['id']

    def test_teacher_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Teacher can view whiteboard."""
        course = Course.find_by_canvas_course_id(
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=1502870,
        )
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard['id'], client=client)
        assert asset['id'] == mock_whiteboard['id']

    def test_student_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Collaborator can view whiteboard created by student in other section."""
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard['id'], client=client)
            assert asset['id'] == mock_whiteboard['id']

    def test_view_whiteboard_protected_per_section(self, client, fake_auth):
        """Collaborator in an asset-siloed course can no longer see whiteboard created by student in other section."""
        course, student_1, whiteboard = _create_student_whiteboard()
        std_commit(allow_test_environment=True)
        student_2 = User.create(
            canvas_course_role='Student',
            canvas_enrollment_state='active',
            canvas_full_name='Hamlet Oxbridge',
            canvas_user_id=858937298,
            course_id=course.id,
            canvas_course_sections=['section B'],
        )
        whiteboard = Whiteboard.update(whiteboard['title'], [student_1, student_2], whiteboard['id'])
        # Expect whiteboard to have two users in two different sections
        users = whiteboard.to_api_json()['users']
        assert len(users) == 2
        assert users[0]['canvasCourseSections'] != users[1]['canvasCourseSections']

        # Enable section siloing
        course.protects_assets_per_section = True
        std_commit(allow_test_environment=True)
        # Verify: the whiteboard goes with student who created it; the other loses access
        fake_auth.login(student_1.id)
        api_json = _api_get_whiteboard(whiteboard_id=whiteboard.id, client=client)
        assert api_json['id'] == whiteboard.id
        fake_auth.login(student_2.id)
        _api_get_whiteboard(whiteboard_id=whiteboard.id, client=client, expected_status_code=404)


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

    def test_inactive_collaborator(self, client, fake_auth):
        course, student_1, whiteboard = _create_student_whiteboard()
        student_2 = User.create(
            canvas_course_role='Student',
            canvas_enrollment_state='active',
            canvas_full_name='Inactive Ira',
            canvas_user_id=958437621,
            course_id=course.id,
        )
        # Expect two active users
        whiteboard = Whiteboard.update(whiteboard['title'], [student_1, student_2], whiteboard['id'])
        assert len(whiteboard.to_api_json()['users']) == 2
        # Make inactive
        inactive_student_2 = User.find_by_id(student_2.id)
        inactive_student_2.canvas_enrollment_state = 'inactive'
        db.session.add(inactive_student_2)
        std_commit(allow_test_environment=True)
        # Verify: the inactive student is effectively dropped
        whiteboard = Whiteboard.update(whiteboard.title, [student_1, student_2], whiteboard.id)
        assert len(whiteboard.to_api_json()['users']) == 1

    def test_authorized(self, client, fake_auth):
        """Get all whiteboards."""
        course, student, whiteboard = _create_student_whiteboard()
        assert student.id in [user['id'] for user in whiteboard['users']]

        # Deleted whiteboard
        deleted_whiteboard = Whiteboard.create(
            course_id=course.id,
            created_by=student.id,
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
            socket_id = str(randint(1, 9999999))
            whiteboard_id = whiteboard['id']
            WhiteboardSession.update_updated_at(
                socket_id=socket_id,
                user_id=user.id,
                whiteboard_id=whiteboard_id,
            )
            std_commit(allow_test_environment=True)

            api_json = self._api_get_whiteboards(
                client=client,
                include_deleted=True,
                order_by='collaborator',
            )
            whiteboards = api_json['results']
            assert len(whiteboards) == api_json['total']

            whiteboards_deleted = next((w for w in whiteboards if w['deletedAt']), [])
            if is_admin(user) or is_teaching(user):
                assert len(whiteboards_deleted)
            else:
                assert len(whiteboards_deleted) == 0

    def test_creator_changes_section(self, client, fake_auth):
        """Student in an asset-siloed course who changes section takes their whiteboards with them."""
        course, student_1, whiteboard = _create_student_whiteboard()
        course.protects_assets_per_section = True
        std_commit(allow_test_environment=True)
        student_2 = User.create(
            canvas_course_role='Student',
            canvas_enrollment_state='active',
            canvas_full_name='McGeorge Pie',
            canvas_user_id=426910492,
            course_id=course.id,
            canvas_course_sections=['section A'],
        )
        whiteboard = Whiteboard.update(whiteboard['title'], [student_1, student_2], whiteboard['id'])
        # Expect whiteboard to have two users in the same section
        users = whiteboard.to_api_json()['users']
        assert len(users) == 2
        assert users[0]['canvasCourseSections'] == ['section A']
        assert users[1]['canvasCourseSections'] == ['section A']
        # The user who created the whiteboard swiches to a different section
        section_b_student = User.find_by_id(student_1.id)
        section_b_student.canvas_course_sections = ['section B']
        db.session.add(section_b_student)
        std_commit(allow_test_environment=True)

        # Verify: the whiteboard goes with student who created it; the other loses access
        fake_auth.login(section_b_student.id)
        api_json = self._api_get_whiteboards(
            client=client,
            order_by='collaborator',
        )
        whiteboards = api_json['results']
        assert len(whiteboards) == api_json['total']
        assert len(whiteboards) == 1
        fake_auth.login(student_2.id)
        api_json = self._api_get_whiteboards(
            client=client,
            order_by='collaborator',
        )
        whiteboards = api_json['results']
        assert len(whiteboards) == api_json['total']
        assert len(whiteboards) == 0

    def test_view_whiteboard_protected_per_section(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Student in an asset-siloed course cannot view whiteboard created by student in other section."""
        mock_whiteboard_course.protects_assets_per_section = True
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            api_json = self._api_get_whiteboards(
                client=client,
                order_by='collaborator',
            )
            expected_count = 1 if collaborator['id'] == mock_whiteboard['createdBy'] else 0
            whiteboards = api_json['results']
            assert len(whiteboards) == api_json['total']
            assert len(whiteboards) == expected_count


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
        uuid = str(uuid4())
        WhiteboardElement.create(
            element={
                'fontSize': 14,
                'uuid': uuid,
            },
            uuid=uuid,
            whiteboard_id=whiteboard['id'],
            z_index=len(whiteboard['whiteboardElements']),
        )
        std_commit(allow_test_environment=True)
        with mock_s3_bucket(app):
            api_json = self._api_export(
                client,
                title='A is for Asset.',
                whiteboard_id=whiteboard['id'],
            )
            asset_id = api_json['id']
            assert asset_id
            for user in api_json['users']:
                activities = Activity.find_by_object_id(object_type='asset', object_id=asset_id)
                add_asset_activities = list(filter(lambda a: a.activity_type == 'whiteboard_export', activities))
                assert len(add_asset_activities) == 1
                assert add_asset_activities[0].user_id == user['id']

    def test_export_whiteboard_protected_per_section(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Student in an asset-siloed course cannot export whiteboard created by student in other section."""
        mock_whiteboard_course.protects_assets_per_section = True
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            self._api_export(
                client,
                expected_status_code=200 if collaborator['id'] == mock_whiteboard['createdBy'] else 404,
                title='Asset of a section A student',
                whiteboard_id=mock_whiteboard['id'],
            )


class TestUndeleteWhiteboard:

    @staticmethod
    def _api_undelete_whiteboard(client, whiteboard_id, expected_status_code=200):
        response = client.post(
            f'/api/whiteboard/{whiteboard_id}/undelete',
            data=json.dumps({'socketId': _get_mock_socket_id()}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        self._api_undelete_whiteboard(client, whiteboard_id=mock_whiteboard['id'], expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_undelete_whiteboard(client, whiteboard_id=mock_whiteboard['id'], expected_status_code=401)

    def test_authorized(self, authorized_user_id, client, fake_auth, mock_whiteboard):
        """Authorized user can un-delete whiteboard."""
        fake_auth.login(authorized_user_id)
        Whiteboard.delete(mock_whiteboard['id'])
        std_commit(allow_test_environment=True)
        api_json = self._api_undelete_whiteboard(client, whiteboard_id=mock_whiteboard['id'])
        assert api_json['deletedAt'] is None
        assert client.get(f"/api/whiteboard/{mock_whiteboard['id']}").json['deletedAt'] is None

    def test_undelete_whiteboard_protected_per_section(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Student in an asset-siloed course cannot undelete whiteboard created by student in other section."""
        mock_whiteboard_course.protects_assets_per_section = True
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            self._api_undelete_whiteboard(
                client,
                expected_status_code=200 if collaborator['id'] == mock_whiteboard['createdBy'] else 404,
                whiteboard_id=mock_whiteboard['id'],
            )


class TestGetEligibleCollaborators:

    @classmethod
    def _api_eligible_collaborators(cls, client, expected_status_code=200):
        response = client.get('/api/whiteboards/eligible_collaborators')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_eligible_collaborators(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_eligible_collaborators(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth, authorized_user_id):
        """Authorized user can get /students_by_section."""
        fake_auth.login(authorized_user_id)
        current_user = User.find_by_id(authorized_user_id)
        eligible_collaborators = self._api_eligible_collaborators(client)
        user_count = len(eligible_collaborators)
        assert user_count > 1
        users_of_all_types = User.get_users_by_course_id(course_id=current_user.course.id)
        assert user_count == len(users_of_all_types)

    def test_course_all_users(self, client, fake_auth, mock_asset_course):
        """Teachers and students can see other users in the course."""
        # Instructor can see all users in the course
        instructor = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Teacher').first()
        fake_auth.login(instructor.id)
        api_json = self._api_eligible_collaborators(client)
        users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
        roles = list(users_by_role.keys())
        assert 'Student' in roles
        assert 'Teacher' in roles

        users_by_section = {section: users for section, users in groupby(
            api_json,
            key=lambda u: u['canvasCourseSections'][0] if u['canvasCourseSections'] and len(u['canvasCourseSections']) else None,
        )}
        sections = list(users_by_section.keys())
        assert 'section A' in sections
        assert 'section B' in sections

        # Students can see all users in the course
        for section in ('section A', 'section B'):
            student = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Student', canvas_course_sections=[section]).first()
            fake_auth.login(student.id)
            api_json = self._api_eligible_collaborators(client)
            users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
            roles = list(users_by_role.keys())
            assert 'Student' in roles
            assert 'Teacher' in roles

            users_by_section = {section: users for section, users in groupby(
                api_json,
                key=lambda u: u['canvasCourseSections'][0] if u['canvasCourseSections'] and len(u['canvasCourseSections']) else None,
            )}
            sections = list(users_by_section.keys())
            assert 'section A' in sections
            assert 'section B' in sections

    def test_course_users_per_section(self, client, fake_auth, mock_asset_course):
        """Students in an asset-siloed course can see only other students in their section."""
        mock_asset_course.protects_assets_per_section = True
        # Instructor can see all users in the course
        instructor = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Teacher').first()
        fake_auth.login(instructor.id)
        api_json = self._api_eligible_collaborators(client)
        users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
        roles = list(users_by_role.keys())
        assert 'Student' in roles
        assert 'Teacher' in roles

        users_by_section = {section: users for section, users in groupby(
            api_json,
            key=lambda u: u['canvasCourseSections'][0] if u['canvasCourseSections'] and len(u['canvasCourseSections']) else None,
        )}
        sections = list(users_by_section.keys())
        assert 'section A' in sections
        assert 'section B' in sections

        # Students can see only instructors plus other users in their section
        for section in ('section A', 'section B'):
            student = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Student', canvas_course_sections=[section]).first()
            fake_auth.login(student.id)
            api_json = self._api_eligible_collaborators(client)
            users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
            roles = list(users_by_role.keys())
            assert 'Student' in roles
            assert 'Teacher' in roles

            users_by_section = {section: users for section, users in groupby(
                api_json,
                key=lambda u: u['canvasCourseSections'][0] if u['canvasCourseSections'] and len(u['canvasCourseSections']) else None,
            )}
            sections = set(users_by_section.keys())
            assert sections == {None, section}


class TestRemixWhiteboard:

    @staticmethod
    def _api_remix_whiteboard(
        client,
        asset_id,
        title,
        expected_status_code=200,
    ):
        response = client.post(
            '/api/whiteboard/remix',
            content_type='application/json',
            data=json.dumps({'assetId': asset_id, 'title': title}),
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_remix_whiteboard(client, asset_id=1, expected_status_code=401, title='Anonymous remix')

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_remix_whiteboard(client, asset_id=1, expected_status_code=401, title='Unauthorized remix')

    def test_authorized(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Authorized user can remix whiteboard."""
        student_id = mock_whiteboard['users'][0]['id']
        fake_auth.login(student_id)
        whiteboard_id = mock_whiteboard['id']
        title = 'Remix me'
        response = client.post(
            f'/api/whiteboard/{whiteboard_id}/export/asset',
            data=json.dumps({'title': title}),
            content_type='application/json',
        )
        assert response.status_code == 200
        asset_original = json.loads(response.data)
        assert asset_original['title'] == title

        student = User.find_by_id(student_id)
        some_other_student = User.find_by_canvas_user_id(4328765)
        assert some_other_student.id != student.id

        for user in [student, some_other_student]:
            logout_user()
            fake_auth.login(user.id)
            custom_title = f'{user.canvas_full_name} remix'
            remixed_whiteboard = self._api_remix_whiteboard(
                client,
                asset_id=asset_original['id'],
                title=custom_title,
            )
            std_commit(allow_test_environment=True)
            assert remixed_whiteboard['title'] == custom_title
            # Compare elements
            original_whiteboard_elements = mock_whiteboard['whiteboardElements']
            remixed_elements = remixed_whiteboard['whiteboardElements']
            assert len(remixed_elements) == len(original_whiteboard_elements)

            def _find_asset_element(elements):
                return next((e for e in elements if e['assetId']), None)

            original_asset_element = _find_asset_element(original_whiteboard_elements)
            remixed_asset_element = _find_asset_element(remixed_elements)
            asset_id = remixed_asset_element['assetId']
            assert asset_id is not None
            assert original_asset_element['assetId'] == asset_id
            assert original_asset_element['uuid'] != remixed_asset_element['uuid']

        activities = Activity.find_by_object_id(object_type='asset', object_id=asset_original['id'])
        # Only the "other" user gets points for 'whiteboard_remix'
        activities_whiteboard_remix = list(filter(lambda a: a.activity_type == 'whiteboard_remix', activities))
        assert len(activities_whiteboard_remix) == 1
        assert activities_whiteboard_remix[0].user_id == some_other_student.id
        # Our student only gets 'get_whiteboard_remix' points when some other student does the remix.
        activities_get_whiteboard_remix = list(filter(lambda a: a.activity_type == 'get_whiteboard_remix', activities))
        assert len(activities_get_whiteboard_remix) == 2

        collaborator_user_ids = [u['id'] for u in mock_whiteboard['users']]
        assert len(activities_get_whiteboard_remix) == len(collaborator_user_ids)
        for activity in activities_get_whiteboard_remix:
            assert activity.user_id in collaborator_user_ids

    def test_undelete_whiteboard_protected_per_section(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Student in an asset-siloed course cannot remix whiteboard created by student in other section."""
        mock_whiteboard_course.protects_assets_per_section = True
        whiteboard_id = mock_whiteboard['id']
        whiteboard_owner_id = mock_whiteboard['createdBy']
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']

        fake_auth.login(whiteboard_owner_id)
        response = client.post(
            f'/api/whiteboard/{whiteboard_id}/export/asset',
            data=json.dumps({'title': 'Exported whiteboard'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        asset_original = json.loads(response.data)

        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            self._api_remix_whiteboard(
                client,
                expected_status_code=200 if collaborator['id'] == whiteboard_owner_id else 404,
                asset_id=asset_original['id'],
                title=f'Remix of original by user_id={whiteboard_owner_id}',
            )


class TestDeleteWhiteboard:

    @staticmethod
    def _api_delete_whiteboard(whiteboard_id, client, expected_status_code=200):
        response = client.delete(f'/api/whiteboard/{whiteboard_id}/delete?socketId=${_get_mock_socket_id()}')
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_delete_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_delete_whiteboard(whiteboard_id=1, client=client, expected_status_code=401)

    def test_delete_whiteboard_by_teacher(self, client, fake_auth, mock_whiteboard):
        """Authorized user can delete whiteboard."""
        course = Course.find_by_canvas_course_id(
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=1502870,
        )
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        whiteboard_id = mock_whiteboard['id']
        self._api_delete_whiteboard(whiteboard_id=whiteboard_id, client=client)
        std_commit(allow_test_environment=True)
        response = client.get(f'/api/whiteboard/{whiteboard_id}')
        assert response.status_code == 200
        assert response.json['deletedAt']


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
        canvas_course_sections=['section A'],
    )
    whiteboard = Whiteboard.create(
        course_id=course.id,
        created_by=student.id,
        title='CyberCulture',
        users=[student],
    )
    return course, student, whiteboard


def _get_mock_socket_id():
    return str(randint(1, 9999999))


def _get_sample_user(canvas_course_role, course):
    return next((u for u in course.users if u.canvas_course_role == canvas_course_role), None)
