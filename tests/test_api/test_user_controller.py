"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from squiggy.lib.util import is_teaching
from squiggy.models.course import Course
from squiggy.models.user import User

unauthorized_user_id = '666'


def _api_my_profile(client, expected_status_code=200):
    response = client.get('/api/profile/my')
    assert response.status_code == expected_status_code
    return response.json


def _api_update_looking_for_collaborators(client, data, expected_status_code=200):
    response = client.post(
        '/api/users/me/looking_for_collaborators',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_update_personal_description(client, data, expected_status_code=200):
    response = client.post(
        '/api/users/me/personal_description',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_update_share_points(client, data, expected_status_code=200):
    response = client.post(
        '/api/users/me/share',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


class TestMyProfile:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        api_json = _api_my_profile(client)
        assert not api_json['isAuthenticated']
        assert not api_json['isAdmin']
        assert not api_json.get('id')
        assert not api_json.get('course')
        assert not api_json.get('canvasGroupMemberships')

    def test_admin_profile(self, client, fake_auth):
        admin = User.query.filter_by(canvas_course_role='Administrator', canvas_enrollment_state='active').first()
        expected_canvas_api_domain = 'bcourses.berkeley.edu'

        fake_auth.login(admin.id)
        api_json = _api_my_profile(client)
        assert api_json['id'] == admin.id
        assert api_json['canvasApiDomain'] == expected_canvas_api_domain
        assert api_json['canvasGroupMemberships'] == []
        assert api_json['isAdmin'] is True
        assert api_json['isAuthenticated'] is True
        assert api_json['isObserver'] is False
        assert api_json['isStudent'] is False
        assert api_json['isTeaching'] is False

        course = Course.find_by_id(admin.course_id).to_api_json()
        assert course
        canvas = course.get('canvas')
        assert canvas
        assert canvas['canvasApiDomain'] == expected_canvas_api_domain

    def test_student_profile(self, client, fake_auth, mock_course_group):
        canvas_user_id = mock_course_group.memberships[0].canvas_user_id
        student = User.find_by_canvas_user_id(canvas_user_id)
        fake_auth.login(student.id)
        api_json = _api_my_profile(client)
        assert api_json['id'] == student.id
        course_groups = api_json['canvasGroupMemberships']
        assert len(course_groups) == 1
        print(course_groups)
        assert course_groups[0]['canvasUserId'] == canvas_user_id
        assert course_groups[0]['categoryName'] == 'Happy Days Televisual Universe (HDTU)'
        assert course_groups[0]['canvasGroupName'] == 'Laverne & Shirley'
        assert course_groups[0]['courseId'] == mock_course_group.course_id
        assert api_json['isAdmin'] is False
        assert api_json['isAuthenticated'] is True
        assert api_json['isObserver'] is False
        assert api_json['isStudent'] is True
        assert api_json['isTeaching'] is False

    def test_teacher_profile(self, client, fake_auth, mock_course_group):
        course = mock_course_group.course
        teacher = list(filter(lambda u: is_teaching(u), course.users))[0]
        fake_auth.login(teacher.id)
        api_json = _api_my_profile(client)
        assert api_json['id'] == teacher.id
        assert api_json['canvasGroupMemberships'] == []
        assert api_json['isAdmin'] is False
        assert api_json['isAuthenticated'] is True
        assert api_json['isObserver'] is False
        assert api_json['isStudent'] is False
        assert api_json['isTeaching'] is True
        assert 'course' not in api_json


class TestGetUsers:
    """User API."""

    @classmethod
    def _api_get_users(cls, client, expected_status_code=200):
        response = client.get('/api/users')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_users(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_users(client, expected_status_code=401)

    def test_admin(self, client, fake_auth, authorized_user_id):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_get_users(client)
        assert len(api_json) > 1
        assert 'id' in api_json[0]
        assert 'canvasFullName' in api_json[0]
        assert 'points' not in api_json[0]
        assert api_json[0]['canvasFullName'] < api_json[1]['canvasFullName']

    def test_only_active_users(self, client, fake_auth, authorized_user_id):
        fake_auth.login(authorized_user_id)
        api_json = self._api_get_users(client)
        for user in api_json:
            assert user['canvasEnrollmentState'] == 'active' or user['canvasEnrollmentState'] == 'invited'

    def test_course_all_users(self, client, fake_auth, mock_asset_course):
        """Teachers and students can see other users in the course."""
        # Instructor can see all users in the course
        instructor = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Teacher').first()
        fake_auth.login(instructor.id)
        api_json = self._api_get_users(client)
        users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
        roles = list(users_by_role.keys())
        assert 'Student' in roles
        assert 'Teacher' in roles

        users_by_section = {section: users for section, users in groupby(
            api_json,
            key=lambda u: u['canvasCourseSections'][0] if len(u['canvasCourseSections']) else None,
        )}
        sections = list(users_by_section.keys())
        assert 'section A' in sections
        assert 'section B' in sections

        # Students can see all users in the course
        for section in ('section A', 'section B'):
            student = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Student', canvas_course_sections=[section]).first()
            fake_auth.login(student.id)
            api_json = self._api_get_users(client)
            users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
            roles = list(users_by_role.keys())
            assert 'Student' in roles
            assert 'Teacher' in roles

            users_by_section = {section: users for section, users in groupby(
                api_json,
                key=lambda u: u['canvasCourseSections'][0] if len(u['canvasCourseSections']) else None,
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
        api_json = self._api_get_users(client)
        users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
        roles = list(users_by_role.keys())
        assert 'Student' in roles
        assert 'Teacher' in roles

        users_by_section = {section: users for section, users in groupby(
            api_json,
            key=lambda u: u['canvasCourseSections'][0] if len(u['canvasCourseSections']) else None,
        )}
        sections = list(users_by_section.keys())
        assert 'section A' in sections
        assert 'section B' in sections

        # Students can see only instructors plus other users in their section
        for section in ('section A', 'section B'):
            student = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Student', canvas_course_sections=[section]).first()
            fake_auth.login(student.id)
            api_json = self._api_get_users(client)
            users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
            roles = list(users_by_role.keys())
            assert 'Student' in roles
            assert 'Teacher' in roles

            users_by_section = {section: users for section, users in groupby(
                api_json,
                key=lambda u: u['canvasCourseSections'][0] if len(u['canvasCourseSections']) else None,
            )}
            sections = list(users_by_section.keys())
            assert set(sections) == set([None, section])


class TestGetLeaderboard:
    """User API."""

    @classmethod
    def _api_get_leaderboard(cls, client, expected_status_code=200):
        response = client.get('/api/users/leaderboard')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_leaderboard(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_leaderboard(client, expected_status_code=401)

    def test_teacher(self, client, fake_auth, authorized_user_id):
        """Returns all users to teacher, including those not sharing points."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_get_leaderboard(client)
        assert len(api_json) > 1
        assert 'id' in api_json[0]
        assert 'canvasFullName' in api_json[0]
        assert 'points' in api_json[0]
        assert api_json[0]['points'] > api_json[1]['points']
        assert next(feed for feed in api_json if not feed['sharePoints'])

    def test_sharing_student(self, client, fake_auth, student_id):
        """Returns sharing students to student user."""
        fake_auth.login(student_id)
        _api_update_share_points(client, {'share': True})
        api_json = self._api_get_leaderboard(client)
        for feed in api_json:
            assert 'points' in feed

    def test_non_sharing_student(self, client, fake_auth, student_id):
        """Denies non-sharing student user."""
        fake_auth.login(student_id)
        _api_update_share_points(client, {'share': False})
        self._api_get_leaderboard(client, expected_status_code=403)

    def test_course_all_users(self, client, fake_auth, mock_asset_course):
        """Teachers and students can see other users in the course."""
        # Instructor can see all users in the course
        instructor = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Teacher').first()
        fake_auth.login(instructor.id)
        _api_update_share_points(client, {'share': True})
        api_json = self._api_get_leaderboard(client)
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

        section_a_student = User.query.filter_by(
            course_id=mock_asset_course.id,
            canvas_course_role='Student',
            canvas_course_sections=['section A'],
        ).first()
        fake_auth.login(section_a_student.id)
        _api_update_share_points(client, {'share': True})
        section_b_student = User.query.filter_by(
            course_id=mock_asset_course.id,
            canvas_course_role='Student',
            canvas_course_sections=['section B'],
        ).first()
        fake_auth.login(section_b_student.id)
        _api_update_share_points(client, {'share': True})

        # Students can see other sharing students in the course
        for student in (section_a_student, section_b_student):
            fake_auth.login(student.id)
            _api_update_share_points(client, {'share': True})
            api_json = self._api_get_leaderboard(client)
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
        api_json = self._api_get_leaderboard(client)
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

        section_a_student = User.query.filter_by(
            course_id=mock_asset_course.id,
            canvas_course_role='Student',
            canvas_course_sections=['section A'],
        ).first()
        fake_auth.login(section_a_student.id)
        _api_update_share_points(client, {'share': True})
        section_b_student = User.query.filter_by(
            course_id=mock_asset_course.id,
            canvas_course_role='Student',
            canvas_course_sections=['section B'],
        ).first()
        fake_auth.login(section_b_student.id)
        _api_update_share_points(client, {'share': True})

        # Students can see only sharing students in their section
        for student in (section_a_student, section_b_student):
            fake_auth.login(student.id)
            api_json = self._api_get_leaderboard(client)
            users_by_role = {role: users for role, users in groupby(api_json, key=lambda u: u['canvasCourseRole'])}
            roles = list(users_by_role.keys())
            assert 'Student' in roles
            assert 'Teacher' in roles

            users_by_section = {section: users for section, users in groupby(
                api_json,
                key=lambda u: u['canvasCourseSections'][0] if u['canvasCourseSections'] and len(u['canvasCourseSections']) else None,
            )}
            sections = list(users_by_section.keys())
            assert set(sections) == set([None, student.canvas_course_sections[0]])


class TestUpdateLookingForCollaborators:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_looking_for_collaborators(client, {'lookingForCollaborators': True}, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_update_looking_for_collaborators(client, {'lookingForCollaborators': True}, expected_status_code=401)

    def test_bad_data(self, client, fake_auth, authorized_user_id):
        """Rejects bad data."""
        fake_auth.login(authorized_user_id)
        _api_update_looking_for_collaborators(client, {'regrettable': 'junk'}, expected_status_code=400)

    def test_toggles_looking_for_collaborators(self, client, fake_auth, authorized_user_id):
        """Turns looking for collaborators on and off."""
        fake_auth.login(authorized_user_id)
        profile = _api_my_profile(client)
        assert profile['lookingForCollaborators'] is False
        response = _api_update_looking_for_collaborators(client, {'lookingForCollaborators': True})
        assert response['lookingForCollaborators'] is True
        profile = _api_my_profile(client)
        assert profile['lookingForCollaborators'] is True
        response = _api_update_looking_for_collaborators(client, {'lookingForCollaborators': False})
        assert response['lookingForCollaborators'] is False
        profile = _api_my_profile(client)
        assert profile['lookingForCollaborators'] is False


class TestUpdatePersonalDescription:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_personal_description(client, {'personalDescription': 'The fastest gun alive'}, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_update_personal_description(client, {'personalDescription': 'The fastest gun alive'}, expected_status_code=401)

    def test_bad_data(self, client, fake_auth, authorized_user_id):
        """Rejects bad data."""
        fake_auth.login(authorized_user_id)
        _api_update_personal_description(client, {'regrettable': 'junk'}, expected_status_code=400)

    def test_set_personal_description(self, client, fake_auth, authorized_user_id):
        """Sets and unsets personal description."""
        fake_auth.login(authorized_user_id)
        profile = _api_my_profile(client)
        assert profile['personalDescription'] is None
        response = _api_update_personal_description(client, {'personalDescription': 'The fastest gun alive'})
        assert response['personalDescription'] == 'The fastest gun alive'
        profile = _api_my_profile(client)
        assert profile['personalDescription'] == 'The fastest gun alive'
        response = _api_update_personal_description(client, {'personalDescription': None})
        assert response['personalDescription'] is None
        profile = _api_my_profile(client)
        assert profile['personalDescription'] is None

    def test_text_exceeds_max_length(self, client, fake_auth, authorized_user_id):
        """Truncates the provided text at 255 characters."""
        long_text = 'ʬ' * 256
        expected_text = 'ʬ' * 255
        fake_auth.login(authorized_user_id)
        response = _api_update_personal_description(client, {'personalDescription': long_text})
        assert response['personalDescription'] == expected_text
        profile = _api_my_profile(client)
        assert profile['personalDescription'] == expected_text


class TestUpdateSharePoints:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_update_share_points(client, {'share': True}, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_update_share_points(client, {'share': True}, expected_status_code=401)

    def test_bad_data(self, client, fake_auth, authorized_user_id):
        """Rejects bad data."""
        fake_auth.login(authorized_user_id)
        _api_update_share_points(client, {'regrettable': 'junk'}, expected_status_code=400)

    def test_toggles_share_points(self, client, fake_auth, authorized_user_id):
        """Turns sharing on and off."""
        fake_auth.login(authorized_user_id)
        _api_update_share_points(client, {'share': False})
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is False
        response = _api_update_share_points(client, {'share': True})
        assert response['sharePoints'] is True
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is True
        response = _api_update_share_points(client, {'share': False})
        assert response['sharePoints'] is False
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is False
