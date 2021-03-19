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

from squiggy.lib.errors import ResourceNotFoundError
from squiggy.lib.util import to_int
from squiggy.models.canvas import Canvas


def lti_launch(args, headers):
    lti_configs = {}
    validation = {
        'custom_canvas_api_domain': _str_strip,
        'custom_canvas_course_id': to_int,
        'custom_canvas_user_id': to_int,
        'custom_external_tool_url': _canvas_external_tool_url,
        'lis_person_name_full': _str_strip,
        'oauth_consumer_key': _alpha_num_32,
        'oauth_nonce': _alpha_num,
        'oauth_signature': _str_strip,
        'oauth_signature_method': _str_strip,
        'oauth_timestamp': to_int,
        'oauth_version': _str_strip,
        'roles': _str_strip,
    }

    def _fetch(key):
        validate = validation[key]
        validation_needs_headers = validate is _canvas_external_tool_url
        lti_configs[key] = validate(args.get(key), headers) if validation_needs_headers else validate(args.get(key))
        return lti_configs[key]

    if all(_fetch(key) for key in validation.keys()):
        canvas_api_domain = lti_configs['custom_canvas_api_domain']
        canvas = Canvas.find_by_domain(
            canvas_api_domain=canvas_api_domain,
            lti_key=lti_configs['oauth_consumer_key'],
        )
        if canvas:
            # TODO
            port_over_old_suitec_logic()
        else:
            raise ResourceNotFoundError(f'Failed \'canvas\' lookup where canvas_api_domain = {canvas_api_domain}')
    else:
        return None


def _alpha_num(s):
    value = _str_strip(s)
    return value if value.isalnum() else None


def _alpha_num_32(s):
    value = _alpha_num(s)
    return value if (value and len(value) == 32) else None


def _canvas_external_tool_url(s, headers):
    referrer = headers.get('Referer')
    pattern = '/external_tools/(\d+)'
    if re.search(pattern, referrer or ''):
        return referrer
    external_tool_url = (_str_strip(s) or '').replace('api/v1/', '')
    return external_tool_url if re.search(pattern, external_tool_url) else None


def _str_strip(s):
    return str(s).strip() if isinstance(s, str) else None


def port_over_old_suitec_logic():
    # TODO:
    #
    #     // Validate the LTI keys
    #     var provider = new lti.Provider(consumer_key, canvas.lti_secret);
    #     provider.valid_request(req, function(err, isValid) {
    #       if (err) {
    #         if (err.message === 'Invalid Signature') {
    #           return callback({'code': 401, 'msg': 'Invalid Signature'});
    #         }
    #
    #         log.error({'err': err}, 'An LTI launch resulted in an error');
    #         return callback({'code': 400, 'msg': err.message});
    #       } else if (!isValid) {
    #         log.warn('An LTI launch was invalid');
    #         return callback({'code': 400, 'msg': 'Failed validation'});
    #       }
    #
    #       // Create the course on the fly
    #       var courseInfo = {
    #         'name': req.body.context_title
    #       };
    #       if (externalToolUrl) {
    #         if (toolId === 'assetlibrary') {
    #           courseInfo.assetlibrary_url = externalToolUrl;
    #         } else if (toolId === 'dashboard') {
    #           courseInfo.dashboard_url = externalToolUrl;
    #         } else if (toolId === 'engagementindex') {
    #           courseInfo.engagementindex_url = externalToolUrl;
    #         } else if (toolId === 'whiteboards') {
    #           courseInfo.whiteboards_url = externalToolUrl;
    #         }
    #       }
    #       CourseAPI.getOrCreateCourse(canvas_course_id, canvas, courseInfo, function(err, course) {
    #         if (err) {
    #           return callback(err);
    #         }
    #
    #         // If the LTI launch did not provide a recognized Canvas enrollment state, mark the user inactive to
    #         // keep them from surfacing as a course site member.
    #         if (!_.includes(_.values(CollabosphereConstants.ENROLLMENT_STATE), canvas_enrollment_state)) {
    #           canvas_enrollment_state = 'inactive';
    #         }
    #
    #         // Site admins are likewise considered inactive.
    #         if (_.includes(CollabosphereConstants.ADMIN_ROLES, canvas_course_role)) {
    #           canvas_enrollment_state = 'inactive';
    #         }
    #
    #         // Create the user on the fly
    #         var defaults = {
    #           'canvas_course_role': canvas_course_role,
    #           'canvas_full_name': canvas_full_name,
    #           'canvas_image': canvas_image,
    #           'canvas_email': canvas_email,
    #           'canvas_enrollment_state': canvas_enrollment_state
    #         };
    #         UsersAPI.getOrCreateUser(canvas_user_id, course, defaults, function(err, user) {
    #           if (err) {
    #             return callback(err);
    #           }
    #
    #           // Store or update the user's analytics properties
    #           AnalyticsAPI.identifyUser(user);
    #
    #           // Keep track of the URL that is performing the LTI launch
    #           provider.body.tool_url = externalToolUrl;
    #
    #           // Keep track of whether this Canvas instance supports custom cross-window messaging
    #           provider.body.supports_custom_messaging = canvas.supports_custom_messaging;
    #
    #           return callback(null, provider.body, user);
    #         });
    #       });
    #     });
    #
    pass
