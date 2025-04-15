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

from squiggy.lib.util import is_teaching
from squiggy.models.course import Course
from squiggy.models.user import User

unauthorized_user_id = '666'


def _api_my_profile(client, expected_status_code=200):
    response = client.get('/api/profile/my')
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
