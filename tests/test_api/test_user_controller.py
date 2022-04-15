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


unauthorized_user_id = '666'


def _api_my_profile(client, expected_status_code=200):
    response = client.get('/api/profile/my')
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

    def test_admin_profile(self, client, fake_auth, authorized_user_id):
        fake_auth.login(authorized_user_id)
        api_json = _api_my_profile(client)
        assert api_json['id'] == authorized_user_id
        course = api_json.get('course')
        assert course
        canvas = course.get('canvas')
        assert canvas
        assert canvas['canvasApiDomain'] == 'bcourses.berkeley.edu'


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


class TestStudentsBySection:

    @classmethod
    def _api_get_students_by_section(cls, client, expected_status_code=200):
        response = client.get('/api/users/students_by_section')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_students_by_section(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_students_by_section(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth, authorized_user_id):
        """Authorized user can get /students_by_section."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_get_students_by_section(client)
        assert len(api_json) > 1
        assert 'header' in api_json[0]
        assert 'canvasFullName' in api_json[1]


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
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is None
        response = _api_update_share_points(client, {'share': True})
        assert response['sharePoints'] is True
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is True
        response = _api_update_share_points(client, {'share': False})
        assert response['sharePoints'] is False
        profile = _api_my_profile(client)
        assert profile['sharePoints'] is False
