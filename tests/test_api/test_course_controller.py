"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from squiggy.models.course import Course
from squiggy.models.user import User


unauthorized_user_id = '666'


def _api_activate_course(client, expected_status_code=200):
    response = client.post('/api/course/activate')
    assert response.status_code == expected_status_code


def _api_get_course(client, course_id, expected_status_code=200):
    response = client.get(f'/api/course/{course_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestReactivateCourse:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_activate_course(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_activate_course(client, expected_status_code=401)

    def test_student(self, client, fake_auth, student_id):
        """Denies student."""
        fake_auth.login(student_id)
        _api_activate_course(client, expected_status_code=401)

    def test_teacher(self, client, fake_auth, authorized_user_id, db_session):
        """Allows teacher."""
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(authorized_user_id)
        api_json = _api_get_course(client, user.course_id)
        assert api_json['active'] is True

        course_id = api_json['id']
        assert course_id == user.course_id
        course = db_session.query(Course).filter_by(id=course_id).first()
        course.active = False
        assert _api_get_course(client, course_id)['active'] is False

        _api_activate_course(client)
        assert _api_get_course(client, course_id)['active'] is True


class TestGetCourse:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_course(client, course_id=1, expected_status_code=401)

    def test_student(self, client, fake_auth, student_id):
        """Authenticated user succeeds."""
        user = User.find_by_id(student_id)
        fake_auth.login(user.id)
        api_json = _api_get_course(client, user.course_id)
        assert user.id in [user['id'] for user in api_json['users']]


class TestProtectsAssetsPerSection:

    def _api_protect_assets_per_section(
            self,
            client,
            protect_assets_per_section,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/course/update_protect_assets_per_section',
            data=json.dumps({
                'protectSectionCheckbox': protect_assets_per_section,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_protect_assets_per_section(
            client=client,
            protect_assets_per_section=True,
            expected_status_code=401,
        )

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_protect_assets_per_section(
            client=client,
            protect_assets_per_section=True,
            expected_status_code=401,
        )

    def test_student(self, client, fake_auth, student_id):
        """Denies student."""
        fake_auth.login(student_id)
        self._api_protect_assets_per_section(
            client=client,
            protect_assets_per_section=True,
            expected_status_code=401,
        )

    def test_teacher(self, client, fake_auth, authorized_user_id, db_session):
        """Allows teacher."""
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(authorized_user_id)
        api_json = _api_get_course(client, user.course_id)
        expected_protect_assets = not api_json['protectsAssetsPerSection']
        self._api_protect_assets_per_section(
            client=client,
            protect_assets_per_section=expected_protect_assets,
        )
        api_json = _api_get_course(client, user.course_id)
        assert api_json['protectsAssetsPerSection'] == expected_protect_assets
