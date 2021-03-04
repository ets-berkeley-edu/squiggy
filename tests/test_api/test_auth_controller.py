"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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

from tests.util import override_config

admin_uid = '2040'
unauthorized_uid = '1015674'


class TestDevAuth:
    """DevAuth handling."""

    @staticmethod
    def _api_dev_auth_login(
            client,
            password,
            uid,
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=123456,
            expected_status_code=200,
    ):
        params = {
            'canvasApiDomain': canvas_api_domain,
            'canvasCourseId': canvas_course_id,
            'password': password,
            'uid': uid,
        }
        response = client.post(
            '/api/auth/dev_auth_login',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_disabled(self, app, client):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            self._api_dev_auth_login(
                client,
                uid=admin_uid,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                expected_status_code=404,
            )

    def test_password_fail(self, app, client):
        """Fails if no match on developer password."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                uid=admin_uid,
                password='Born 2 Lose',
                expected_status_code=401,
            )

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                uid='A Bad Sort',
                expected_status_code=403,
            )

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                uid=unauthorized_uid,
                expected_status_code=403,
            )

    def test_known_user_with_correct_password_logs_in(self, app, client):
        """There is a happy path."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            api_json = self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                uid=admin_uid,
            )
            assert api_json['uid'] == admin_uid
            response = client.post('/api/auth/logout')
            assert response.status_code == 200


class TestAuthorization:

    @staticmethod
    def _api_my_profile(client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_admin_profile(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = self._api_my_profile(client)
        assert api_json['uid'] == admin_uid
