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

from datetime import datetime
import json

from squiggy import db, std_commit
from squiggy.lib.lti import TOOL_ID_ASSET_LIBRARY, TOOL_ID_ENGAGEMENT_INDEX, TOOL_ID_IMPACT_STUDIO, TOOL_ID_WHITEBOARDS
from squiggy.models.canvas import Canvas
from squiggy.models.course import Course
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
        """Fails if the chosen user_id does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                user_id='A Bad Sort',
                expected_status_code=403,
            )

    def test_canvas_enrollment_state(self, app, client):
        """Fails if canvas_enrollment_state is not active."""
        user = User.find_by_canvas_user_id(8765433)
        assert user.canvas_enrollment_state == 'inactive'
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            self._api_dev_auth_login(
                client,
                password=app.config['DEVELOPER_AUTH_PASSWORD'],
                user_id=user.id,
                expected_status_code=403,
            )

    def test_unauthorized_user(self, app, client):
        """Fails if the chosen user_id does not match an authorized user."""
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
            assert api_json['canvasCourseId'] == 1502870
            assert api_json['canvasApiDomain'] == 'bcourses.berkeley.edu'
            assert client.post('/api/auth/logout').status_code == 200


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
            roles,
            tool_id,
            expected_status_code=302,
    ):
        data = {
            'custom_canvas_api_domain': custom_canvas_api_domain,
            'custom_canvas_course_id': custom_canvas_course_id,
            'custom_canvas_user_id': custom_canvas_user_id,
            'custom_external_tool_url': custom_external_tool_url,
            'lis_person_name_full': lis_person_name_full,
            'oauth_consumer_key': oauth_consumer_key,
            'oauth_nonce': 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pT',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(datetime.now().timestamp())),
            'oauth_version': '1.0',
            'roles': roles,
        }
        url = {
            TOOL_ID_ASSET_LIBRARY: '/api/auth/lti_launch/asset_library',
            TOOL_ID_ENGAGEMENT_INDEX: '/api/auth/lti_launch/engagement_index',
            TOOL_ID_IMPACT_STUDIO: '/api/auth/lti_launch/impact_studio',
            TOOL_ID_WHITEBOARDS: '/api/auth/lti_launch/whiteboards',
        }.get(tool_id)
        response = client.post(
            url,
            content_type='application/x-www-form-urlencoded',
            data=data,
            headers={'Referer': custom_external_tool_url},
        )
        assert response.status_code == expected_status_code
        return response

    def test_create_user_at_lti_launch(self, client):
        """User is created during LTI launch."""
        canvas_api_domain = 'bcourses.berkeley.edu'
        canvas = Canvas.find_by_domain(canvas_api_domain=canvas_api_domain)
        canvas_course_id = 2870150
        # Verify that course is NOT in db, yet
        assert not Course.query.filter_by(canvas_course_id=canvas_course_id).first()

        canvas_user_id = 45678901
        full_name = 'Dee Dee Ramone'
        external_tool_url = f'https://bcourses.berkeley.edu/courses/{canvas_course_id}/external_tools/98765'

        def _create_user_at_lti_launch(tool_id):
            _response = self._api_auth_lti_launch(
                client=client,
                custom_canvas_api_domain=canvas.canvas_api_domain,
                custom_canvas_course_id=canvas_course_id,
                custom_canvas_user_id=canvas_user_id,
                custom_external_tool_url=external_tool_url,
                lis_person_name_full=full_name,
                oauth_consumer_key=canvas.lti_key,
                roles='Student',
                tool_id=tool_id,
            )
            std_commit(allow_test_environment=True)

            user = User.find_by_canvas_user_id(canvas_user_id)
            assert user
            assert user.canvas_full_name == full_name
            assert user.canvas_user_id == canvas_user_id

            course = user.course
            assert course.canvas_course_id == canvas_course_id
            if tool_id == TOOL_ID_ASSET_LIBRARY:
                assert course.asset_library_url == external_tool_url
            elif tool_id == TOOL_ID_ENGAGEMENT_INDEX:
                assert course.engagement_index_url == external_tool_url
            elif tool_id == TOOL_ID_IMPACT_STUDIO:
                assert course.impact_studio_url == external_tool_url
            elif tool_id == TOOL_ID_WHITEBOARDS:
                assert course.whiteboards_url == external_tool_url
            return _response

        for tool_id in (TOOL_ID_ASSET_LIBRARY, TOOL_ID_ENGAGEMENT_INDEX, TOOL_ID_IMPACT_STUDIO, TOOL_ID_WHITEBOARDS):
            # Delete
            db.session.execute(f'DELETE FROM users WHERE canvas_user_id = {canvas_user_id}')
            std_commit(allow_test_environment=True)

            response = _create_user_at_lti_launch(tool_id)
            assert f'canvasApiDomain={canvas_api_domain}&canvasCourseId={canvas_course_id}' in response.location
            # Expect no duplicates
            assert len(User.query.filter_by(canvas_user_id=canvas_user_id).all()) == 1
            assert len(Course.query.filter_by(canvas_course_id=canvas_course_id).all()) == 1


class TestCookies:
    """Cookies."""

    @staticmethod
    def _assert_cookie(client, user=None):
        client.get('/api/profile/my')
        cookies = list(client.cookie_jar)
        if user:
            def _assert_cookie_value(key, value):
                cookie = next(c for c in cookies if c.key == key)
                assert cookie
                assert cookie.value == str(value)

            canvas_api_domain = user.course.canvas_api_domain
            canvas = Canvas.find_by_domain(canvas_api_domain)
            _assert_cookie_value(
                key=f'{canvas_api_domain}|{user.course.canvas_course_id}',
                value=user.id,
            )
            _assert_cookie_value(
                key=f'{canvas_api_domain}_supports_custom_messaging',
                value=canvas.supports_custom_messaging,
            )
        else:
            assert 'supports_custom_messaging' not in cookies

    def test_anonymous(self, client):
        """No cookies for anonymous user."""
        self._assert_cookie(client=client)

    def test_unauthorized(self, client, fake_auth):
        """No cookies for unauthorized user."""
        self._assert_cookie(client=client)

    def test_admin(self, client, fake_auth, authorized_user_id):
        """Cookies for authenticated user."""
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        self._assert_cookie(client=client, user=user)


class TestBookmarkletAuth:

    @staticmethod
    def _api_assets_with_bookmarklet_auth(
            client,
            bookmarklet_auth_header,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/assets',
            content_type='application/json',
            data=json.dumps({}),
            headers={'Squiggy-Bookmarklet-Auth': bookmarklet_auth_header},
        )
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """Invalid Squiggy-Bookmarklet-Auth header."""
        self._api_assets_with_bookmarklet_auth(
            client=client,
            bookmarklet_auth_header='this surely cannot be a valid',
            expected_status_code=401,
        )

    def test_authorized_admin(self, app, client):
        """Admin only needs valid Squiggy-Bookmarklet-Auth header value."""
        with app.app_context():
            course = Course.find_by_canvas_course_id(
                canvas_api_domain='bcourses.berkeley.edu',
                canvas_course_id=1502871,
            )
            user = User.create(
                canvas_course_role='Admin',
                canvas_email='admin@berkeley.edu',
                canvas_enrollment_state='inactive',
                canvas_full_name='Jane Admin',
                canvas_user_id='24680',
                course_id=course.id,
            )
            std_commit(allow_test_environment=True)
            # Expect authorized
            bookmarklet_auth = user.to_api_json()['bookmarkletAuth']
            self._api_assets_with_bookmarklet_auth(bookmarklet_auth_header=bookmarklet_auth, client=client)

    def test_authorized_to_unauthorized(self, app, client):
        """Deny Squiggy-Bookmarklet-Auth when course_id does not match."""
        with app.app_context():
            canvas_course_id = 1502871
            course = Course.find_by_canvas_course_id(
                canvas_api_domain='bcourses.berkeley.edu',
                canvas_course_id=canvas_course_id,
            )
            user = User.create(
                canvas_course_role='Student',
                canvas_course_sections=[],
                canvas_email='nico@berkeley.edu',
                canvas_enrollment_state='active',
                canvas_full_name='Nico ',
                canvas_user_id='13579',
                course_id=course.id,
            )
            std_commit(allow_test_environment=True)

            # Expect authorized
            bookmarklet_auth = user.to_api_json()['bookmarkletAuth']
            self._api_assets_with_bookmarklet_auth(bookmarklet_auth_header=bookmarklet_auth, client=client)

            # Student becomes inactive and we try to hack our way in with the old bookmarklet auth header.
            user.canvas_enrollment_state = 'inactive'
            db.session.add(user)
            std_commit(allow_test_environment=True)

            client.post('/api/auth/logout')

            # Expect unauthorized
            self._api_assets_with_bookmarklet_auth(
                bookmarklet_auth_header=bookmarklet_auth,
                client=client,
                expected_status_code=401,
            )


class TestCookieAuth:

    @staticmethod
    def _api_assets_with_cookie_auth(
            canvas_api_domain,
            canvas_course_id,
            client,
            expected_status_code=200,
    ):
        response = client.post(
            '/api/assets',
            content_type='application/json',
            data=json.dumps({}),
            headers={
                'Squiggy-Canvas-Api-Domain': canvas_api_domain,
                'Squiggy-Canvas-Course-Id': str(canvas_course_id),
            },
        )
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """No cookie auth for anonymous user."""
        self._api_assets_with_cookie_auth(
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=1502870,
            client=client,
            expected_status_code=401,
        )

    def test_unauthorized(self, client):
        """No cookie auth for unauthorized user."""
        canvas_course_id = 1502871
        unauthorized_user = User.find_by_canvas_user_id(canvas_user_id=654321)
        assert unauthorized_user
        assert unauthorized_user.course.canvas_course_id != canvas_course_id

        canvas_api_domain = unauthorized_user.course.canvas_api_domain
        client.set_cookie('localhost', f'{canvas_api_domain}|{canvas_course_id}', str(unauthorized_user.id))
        self._api_assets_with_cookie_auth(
            canvas_api_domain=canvas_api_domain,
            canvas_course_id=canvas_course_id,
            client=client,
            expected_status_code=401,
        )

    def test_authorized(self, app, client):
        """Cookie auth for authorized user."""
        with app.app_context():
            canvas_course_id = 1502870
            authorized_user = User.find_by_canvas_user_id(canvas_user_id=654321)
            assert authorized_user
            assert authorized_user.course.canvas_course_id == canvas_course_id

            canvas_api_domain = authorized_user.course.canvas_api_domain
            client.set_cookie('localhost', f'{canvas_api_domain}|{canvas_course_id}', str(authorized_user.id))
            self._api_assets_with_cookie_auth(
                canvas_api_domain=canvas_api_domain,
                canvas_course_id=canvas_course_id,
                client=client,
            )
            # Finally, log out and verify that cookie has been removed.
            assert client.post('/api/auth/logout').status_code == 200
            self._api_assets_with_cookie_auth(
                canvas_api_domain=canvas_api_domain,
                canvas_course_id=canvas_course_id,
                client=client,
                expected_status_code=401,
            )


class TestMasquerade:

    @staticmethod
    def _api_masquerade(client, user_id, expected_status_code=200):
        response = client.post(
            '/api/auth/masquerade',
            data=json.dumps({'userId': user_id}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_disabled(self, app, client, authorized_user_id, fake_auth):
        """Blocks access unless enabled."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            admin = User.find_by_canvas_user_id(321098)
            fake_auth.login(admin.id)
            self._api_masquerade(
                client,
                user_id=authorized_user_id,
                expected_status_code=404,
            )

    def test_unauthorized(self, app, client, fake_auth):
        """Non-admin users are not authorized."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            teacher = User.find_by_canvas_user_id(9876543)
            self._api_masquerade(
                client,
                user_id=teacher.id,
                expected_status_code=401,
            )

    def test_authorized(self, app, client, fake_auth):
        """Fails if the chosen user_id does not match an authorized user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            admin = User.find_by_canvas_user_id(321098)
            fake_auth.login(admin.id)

            teacher = User.find_by_canvas_user_id(9876543)
            masquerading = self._api_masquerade(client, user_id=teacher.id)
            assert masquerading['id'] == teacher.id
