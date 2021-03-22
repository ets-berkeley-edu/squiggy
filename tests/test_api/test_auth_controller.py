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

from datetime import datetime
import json

import pytest
from squiggy.merged.lti import TOOL_ID_ASSET_LIBRARY
from squiggy.models.canvas import Canvas
from squiggy.models.user import User
from tests.util import override_config

unauthorized_user_id = '666'


class TestDevAuth:
    """DevAuth handling."""

    @staticmethod
    def _api_dev_auth_login(
            client,
            password,
            user_id,
            expected_status_code=200,
    ):
        params = {
            'password': password,
            'userId': user_id,
        }
        response = client.post(
            '/api/auth/dev_auth_login',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_disabled(self, app, client, authorized_user_id):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            self._api_dev_auth_login(
                client,
                user_id=authorized_user_id,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                expected_status_code=404,
            )

    def test_password_fail(self, app, client, authorized_user_id):
        """Fails if no match on developer password."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                user_id=authorized_user_id,
                password='Born 2 Lose',
                expected_status_code=401,
            )

    def test_authorized_user_fail(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                user_id='A Bad Sort',
                expected_status_code=403,
            )

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen UID does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                user_id=unauthorized_user_id,
                expected_status_code=403,
            )

    def test_known_user_with_correct_password_logs_in(self, app, client, authorized_user_id):
        """There is a happy path."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            api_json = self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                user_id=authorized_user_id,
            )
            assert api_json['id'] == authorized_user_id
            assert api_json['course']['canvasCourseId'] == 1502870
            assert api_json['course']['canvasApiDomain'] == 'bcourses.berkeley.edu'
            assert client.post('/api/auth/logout').status_code == 200


class TestAuthorization:

    @staticmethod
    def _api_my_profile(client, expected_status_code=200):
        response = client.get('/api/profile/my')
        assert response.status_code == expected_status_code
        return response.json

    def test_admin_profile(self, client, fake_auth, authorized_user_id):
        fake_auth.login(authorized_user_id)
        api_json = self._api_my_profile(client)
        assert api_json['id'] == authorized_user_id


class TestLtiLaunchUrl:
    """LTI Launch API."""

    @staticmethod
    def _api_auth_lti_launch(
            client,
            custom_canvas_api_domain,
            custom_canvas_course_id,
            custom_canvas_user_id,
            custom_external_tool_url,
            lis_person_name_full,
            oauth_consumer_key,
            oauth_consumer_secret,
            roles,
            tool_id,
            expected_status_code=200,
    ):
        data = {
            'custom_canvas_api_domain': custom_canvas_api_domain,
            'custom_canvas_course_id': custom_canvas_course_id,
            'custom_canvas_user_id': custom_canvas_user_id,
            'custom_external_tool_url': custom_external_tool_url,
            'lis_person_name_full': lis_person_name_full,
            'oauth_consumer_key': oauth_consumer_key,
            'oauth_consumer_secret': oauth_consumer_secret,
            'oauth_nonce': 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pT',
            'oauth_signature': '?????',  # TODO: We must solve the mystery of simulating Canvas LTI launch POST.
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(datetime.now().timestamp())),
            'oauth_version': '1.0',
            'roles': roles,
        }
        is_asset_library = tool_id == TOOL_ID_ASSET_LIBRARY
        response = client.post(
            '/api/auth/lti_launch/asset_library' if is_asset_library else '/api/auth/lti_launch/engagement_index',
            data=data,
            content_type='application/x-www-form-urlencoded',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    @pytest.mark.skipif(reason='TODO: We must solve the mystery of simulating Canvas LTI launch POST.')
    def test_create_user_at_lti_launch(self, client):
        """User is created during LTI launch."""
        canvas_api_domain = 'bcourses.berkeley.edu'
        canvas = Canvas.find_by_domain(canvas_api_domain=canvas_api_domain)
        canvas_course_id = 1502870
        canvas_user_id = 45678901
        full_name = 'Dee Dee Ramone'
        self._api_auth_lti_launch(
            client=client,
            custom_canvas_api_domain=canvas.canvas_api_domain,
            custom_canvas_course_id=canvas_course_id,
            custom_canvas_user_id=canvas_user_id,
            custom_external_tool_url=f'https://bcourses.berkeley.edu/courses/{canvas_course_id}/external_tools/98765',
            lis_person_name_full=full_name,
            oauth_consumer_key=canvas.lti_key,
            oauth_consumer_secret=canvas.lti_secret,
            roles='Student',
            tool_id=TOOL_ID_ASSET_LIBRARY,
        )
        user = User.find_by_canvas_user_id(canvas_user_id)
        assert user
        assert user.canvas_full_name == full_name


class TestCookies:
    """Cookies."""

    @pytest.mark.skipif(reason='TODO: Verify that cookies are properly managed.')
    def test_squiggy_cookies(self, client):
        """Cookies are properly managed."""
        pass
