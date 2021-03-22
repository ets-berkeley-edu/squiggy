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

from flask import current_app as app
from lti.contrib.flask import FlaskToolProvider
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.merged.lti_request_validator import LtiRequestValidator
from squiggy.models.canvas import Canvas
from squiggy.models.course import Course
from squiggy.models.user import User

TOOL_ID_ASSET_LIBRARY = 'suitec:asset_library'
TOOL_ID_ENGAGEMENT_INDEX = 'suitec:engagement_index'


def lti_launch(request, tool_id):
    is_asset_library = tool_id == TOOL_ID_ASSET_LIBRARY
    is_engagement_index = tool_id == TOOL_ID_ENGAGEMENT_INDEX
    if not is_asset_library and not is_engagement_index:
        raise BadRequestError(f'Missing or invalid tool_id: {tool_id}')

    user = None
    args = request.form
    lti_configs = {}
    validation = {
        'custom_canvas_api_domain': _str_strip,
        'custom_canvas_course_id': _str_strip,
        'custom_canvas_user_id': _str_strip,
        'custom_external_tool_url': _canvas_external_tool_url,
        'lis_person_name_full': _str_strip,
        'oauth_consumer_key': _alpha_num,
        'oauth_nonce': _alpha_num,
        'oauth_signature': _str_strip,
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
            lti_configs[key] = validated_value
            return lti_configs[key]
        else:
            app.logger.warn(f'Invalid \'{key}\' parameter in LTI launch: {value}')

    if all(_fetch(key) for key in validation.keys()):
        canvas_api_domain = lti_configs['custom_canvas_api_domain']
        canvas = Canvas.find_by_domain(canvas_api_domain)
        if canvas and canvas.lti_key == lti_configs['oauth_consumer_key']:
            # TODO: How does Canvas deliver LTI_SECRET?
            lti_secret = canvas.lti_secret
            tool_metadata = _get_tool_metadata(
                host=request.headers['Host'],
                tool_id=tool_id,
            )
            tool_provider = FlaskToolProvider.from_unpacked_request(
                params=lti_configs,
                url=tool_metadata['launch_url'],
                headers=dict(request.headers),
                secret=lti_secret,
            )
            if tool_provider.is_valid_request(LtiRequestValidator(canvas)):
                external_tool_url = lti_configs['custom_external_tool_url']
                course = Course.find_or_create(
                    asset_library_url=external_tool_url if is_asset_library else None,
                    canvas_api_domain=canvas_api_domain,
                    canvas_course_id=lti_configs['custom_canvas_course_id'],
                    engagement_index_url=external_tool_url if is_engagement_index else None,
                    name=args.get('context_title'),
                )
                user = User.find_or_create(
                    course_id=course.id,
                    canvas_user_id=lti_configs['custom_canvas_user_id'],
                    canvas_course_role='TODO',
                    canvas_enrollment_state='TODO',
                    canvas_full_name='TODO',
                    canvas_image='TODO',
                    canvas_email='TODO',
                    canvas_course_sections='TODO',
                )

            else:
                raise BadRequestError(f'LTI oauth failed in {canvas_api_domain} request')
        else:
            raise ResourceNotFoundError(f'Failed \'canvas\' lookup where canvas_api_domain = {canvas_api_domain}')
    return user, ('/assets' if is_asset_library else '/engage')


def get_lti_cartridge_xml(host, tool_id):
    tool_metadata = _get_tool_metadata(host=host, tool_id=tool_id)
    launch_url = tool_metadata['launch_url']
    title = tool_metadata['title']
    return f"""
        <?xml version="1.0" encoding="UTF-8"?>
            <cartridge_basiclti_link
              xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
              xmlns:blti = "http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
              xmlns:lticm ="http://www.imsglobal.org/xsd/imslticm_v1p0"
              xmlns:lticp ="http://www.imsglobal.org/xsd/imslticp_v1p0"
              xmlns:xsi = "http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation = "
                http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
                http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0.xsd
                http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
                http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
              <blti:title>{title}</blti:title>
              <blti:description>{tool_metadata['description']}</blti:description>
              <blti:launch_url>{launch_url}</blti:launch_url>
              <blti:extensions platform="canvas.instructure.com">
                <lticm:property name="tool_id">{tool_id}</lticm:property>
                <lticm:property name="privacy_level">public</lticm:property>
                <lticm:options name="course_navigation">
                  <lticm:property name="url">{launch_url}</lticm:property>
                  <lticm:property name="text">{title}</lticm:property>
                  <lticm:property name="visibility">public</lticm:property>
                  <lticm:property name="default">disabled</lticm:property>
                  <lticm:property name="enabled">false</lticm:property>
                  <lticm:options name="custom_fields">
                    <lticm:property name="external_tool_url">$Canvas.externalTool.url</lticm:property>
                  </lticm:options>
                </lticm:options>
              </blti:extensions>
              <cartridge_bundle identifierref="BLTI001_Bundle"/>
              <cartridge_icon identifierref="BLTI001_Icon"/>
            </cartridge_basiclti_link>
    """


def _alpha_num(s):
    value = _str_strip(s)
    return value if value.isalnum() else None


def _canvas_external_tool_url(s, headers):
    referrer = headers.get('Referer')
    pattern = '/external_tools/(\d+)'
    if re.search(pattern, referrer or ''):
        return referrer
    external_tool_url = (_str_strip(s) or '').replace('api/v1/', '')
    return external_tool_url if re.search(pattern, external_tool_url) else None


def _get_tool_metadata(host, tool_id):
    is_asset_library = tool_id == TOOL_ID_ASSET_LIBRARY
    api_path = '/api/auth/lti_launch/asset_library' if is_asset_library else '/api/auth/lti_launch/engagement_index'
    launch_url = f"'https://{host.rstrip('/')}{api_path}'"
    return {
        TOOL_ID_ASSET_LIBRARY: {
            'description': """
                The Asset Library is where students and instructors can collect relevant materials for the course.
                Materials can be seen by the other students in the class and can be discussed, liked, etc.
            """,
            'launch_url': launch_url,
            'title': 'Asset Library',
        },
        TOOL_ID_ENGAGEMENT_INDEX: {
            'description': """
                The Engagement Index provides a leaderboard based on the student's activity in the course.
                The Engagement Index will record activities such as discussion posts, likes, comments, etc.
            """,
            'launch_url': launch_url,
            'title': 'Engagement Index',
        },
    }.get(tool_id, None)


def _str_strip(s):
    return str(s).strip() if isinstance(s, str) else None
