"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

import re

from flask import current_app as app, redirect, request
from flask_login import current_user, login_required, login_user, logout_user
from lti.contrib.flask import FlaskToolProvider
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError, UnauthorizedRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.login_session import LoginSession
from squiggy.lib.lti import LtiRequestValidator, TOOL_ID_ASSET_LIBRARY, TOOL_ID_ENGAGEMENT_INDEX
from squiggy.lib.util import to_int
from squiggy.models.canvas import Canvas
from squiggy.models.course import Course
from squiggy.models.user import User


@app.route('/api/auth/dev_auth_login', methods=['POST'])
def dev_auth_login():
    params = request.get_json() or {}
    if app.config['DEVELOPER_AUTH_ENABLED']:
        user_id = to_int(params.get('userId'))
        password = params.get('password')
        logger = app.logger

        if password != app.config['DEVELOPER_AUTH_PASSWORD']:
            logger.error('Dev auth: Wrong password')
            return tolerant_jsonify({'message': 'Invalid credentials'}, 401)
        return _login_user(user_id)
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    response = tolerant_jsonify(current_user.to_api_json())
    # Delete our custom cookies
    canvas_api_domain = current_user.course.canvas_api_domain
    keys = [
        f'{canvas_api_domain}|{current_user.course.canvas_course_id}',
        f'{canvas_api_domain}_supports_custom_messaging',
    ]
    for key in keys:
        response.set_cookie(key, '', expires=0)

    logout_user()
    return response


@app.route('/api/auth/lti_launch/asset_library', methods=['POST'])
def lti_launch_asset_library():
    return _lti_launch(TOOL_ID_ASSET_LIBRARY)


@app.route('/api/auth/lti_launch/engagement_index', methods=['POST'])
def lti_launch_engagement_index():
    return _lti_launch(TOOL_ID_ENGAGEMENT_INDEX)


def _canvas_external_tool_url(s, headers):
    referrer = headers.get('Referer') or ''
    for separator in ('#', '?'):
        referrer = referrer.split(separator)[0]
    pattern = '/external_tools/(\d+)'
    if re.search(pattern, referrer):
        return referrer
    external_tool_url = (_str_strip(s) or '').replace('api/v1/', '')
    return external_tool_url if re.search(pattern, external_tool_url) else None


def _lti_launch(tool_id):
    app.logger.info(f'Begin LTI launch for tool {tool_id}')
    user, redirect_path = _lti_launch_authentication(tool_id=tool_id)
    return _login_user(user_id=user and user.id, redirect_path=redirect_path, tool_id=tool_id)


def _lti_launch_authentication(tool_id):
    is_asset_library = tool_id == TOOL_ID_ASSET_LIBRARY
    is_engagement_index = tool_id == TOOL_ID_ENGAGEMENT_INDEX
    if not is_asset_library and not is_engagement_index:
        raise BadRequestError(f'Missing or invalid tool_id: {tool_id}')

    def _alpha_num(s):
        value = _str_strip(s)
        return value if value.isalnum() else None

    args = request.form
    lti_params = {}
    validation = {
        'custom_canvas_api_domain': _str_strip,
        'custom_canvas_course_id': _str_strip,
        'custom_canvas_user_id': _str_strip,
        'custom_external_tool_url': _canvas_external_tool_url,
        'lis_person_name_full': _str_strip,
        'oauth_consumer_key': _alpha_num,
        'oauth_nonce': _alpha_num,
        'oauth_signature_method': _str_strip,
        'oauth_timestamp': _str_strip,
        'oauth_version': _str_strip,
        'roles': _str_strip,
    }

    def _fetch(key):
        value = args.get(key)
        validate = validation[key]
        pass_headers = validate is _canvas_external_tool_url
        validated_value = validate(value, request.headers) if pass_headers else validate(value)
        if validated_value:
            lti_params[key] = validated_value
            return lti_params[key]
        else:
            app.logger.warning(f'Invalid \'{key}\' parameter in LTI launch: {value}')

    if all(_fetch(key) for key in validation.keys()):
        app.logger.info(f'LTI launch params passed basic validation: {lti_params}')
        canvas_api_domain = lti_params['custom_canvas_api_domain']
        canvas = Canvas.find_by_domain(canvas_api_domain)

        if not canvas:
            raise ResourceNotFoundError(f'Failed \'canvas\' lookup where canvas_api_domain = {canvas_api_domain}')

        if canvas.lti_key != lti_params['oauth_consumer_key']:
            raise BadRequestError(f'oauth_consumer_key does not match {canvas_api_domain} lti_key in squiggy db.')

        tool_provider = FlaskToolProvider.from_flask_request(
            request=request,
            secret=canvas.lti_secret,
        )
        valid_request = tool_provider.is_valid_request(LtiRequestValidator(canvas))

        if valid_request or app.config['TESTING']:
            # TODO: We do not want app.config['TESTING'] in this conditional. It is here because our tests are failing
            #       on HMAC-signature verification. Let's fix after we get a successful LTI launch.
            app.logger.info(f'FlaskToolProvider validated {canvas_api_domain} LTI launch request.')
        else:
            raise BadRequestError(f'LTI oauth failed in {canvas_api_domain} request')

        external_tool_url = lti_params['custom_external_tool_url']
        canvas_course_id = lti_params['custom_canvas_course_id']
        course = Course.find_by_canvas_course_id(
            canvas_api_domain=canvas_api_domain,
            canvas_course_id=canvas_course_id,
        )
        if course:
            course = Course.update(
                asset_library_url=external_tool_url if is_asset_library else course.asset_library_url,
                course_id=course.id,
                engagement_index_url=external_tool_url if is_engagement_index else course.engagement_index_url,
            )
            app.logger.info(f'Updated course during LTI launch: {course.to_api_json()}')
        else:
            course = Course.create(
                asset_library_url=external_tool_url if is_asset_library else None,
                canvas_api_domain=canvas_api_domain,
                canvas_course_id=canvas_course_id,
                engagement_index_url=external_tool_url if is_engagement_index else None,
                name=args.get('context_title'),
            )
            app.logger.info(f'Created course via LTI launch: {course.to_api_json()}')

        canvas_user_id = lti_params['custom_canvas_user_id']
        user = User.find_by_course_id(canvas_user_id=canvas_user_id, course_id=course.id)
        if user:
            app.logger.info(f'Found user during LTI launch: canvas_user_id={canvas_user_id}, course_id={course.id}')
        else:
            user = User.create(
                course_id=course.id,
                canvas_user_id=canvas_user_id,
                canvas_course_role=str(lti_params['roles']),
                canvas_enrollment_state=args.get('custom_canvas_enrollment_state') or 'active',
                canvas_full_name=lti_params['lis_person_name_full'],
                canvas_image=args.get('user_image'),  # TODO: Verify user_image.
                canvas_email=args.get('lis_person_contact_email_primary'),
                canvas_course_sections=None,  # TODO: Set by poller?
            )
            app.logger.info(f'Created user during LTI launch: canvas_user_id={canvas_user_id}')

        # Asset page is bookmark-able
        match = re.search('suitec_assetId=([0-9]+)', request.headers.get('Referer', ''))
        asset_id = match and match.group(1)

        path = f'/asset/{asset_id}' if asset_id else ('/assets' if is_asset_library else '/engage')
        params = f'canvasApiDomain={canvas_api_domain}&canvasCourseId={canvas_course_id}'
        app.logger.info(f'LTI launch redirect: {path}?{params}')
        return user, f'{path}?{params}'


def _login_user(user_id, redirect_path=None, tool_id=None):
    app.logger.info(f'_login_user: user_id={user_id}, redirect_path={redirect_path}, tool_id={tool_id}')
    authenticated = login_user(LoginSession(user_id), remember=True) and current_user.is_authenticated
    if authenticated:
        if redirect_path:
            response = redirect(location=f"{app.config['VUE_LOCALHOST_BASE_URL'] or ''}{redirect_path}")
        else:
            response = tolerant_jsonify(current_user.to_api_json())

        canvas_api_domain = current_user.course.canvas_api_domain
        canvas = Canvas.find_by_domain(canvas_api_domain)
        canvas_course_id = current_user.course.canvas_course_id
        # Yummy cookies!
        key = f'{canvas_api_domain}|{canvas_course_id}'
        value = str(current_user.user_id)
        response.set_cookie(
            key=key,
            value=value,
            samesite='None',
            secure=True,
        )
        app.logger.info(f'_login_user cookie: key={key} value={str(current_user.user_id)}')

        response.set_cookie(
            key=f'{canvas_api_domain}_supports_custom_messaging',
            value=str(canvas.supports_custom_messaging),
            samesite='None',
            secure=True,
        )
        return response
    elif tool_id:
        raise UnauthorizedRequestError(f'Unauthorized user during {tool_id} LTI launch (user_id = {user_id})')
    else:
        return tolerant_jsonify({'message': f'User {user_id} failed to authenticate.'}, 403)


def _str_strip(s):
    return str(s).strip() if isinstance(s, str) else None
