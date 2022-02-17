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

from oauthlib.oauth1 import RequestValidator
from squiggy.models.canvas import Canvas

TOOL_ID_ASSET_LIBRARY = 'suitec:asset_library'
TOOL_ID_ENGAGEMENT_INDEX = 'suitec:engagement_index'
TOOL_ID_WHITEBOARDS = 'suitec:whiteboards'


class LtiRequestValidator(RequestValidator):

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas

    def get_client_secret(self, client_key, request):
        return self.canvas.lti_secret

    def validate_client_key(self, client_key, request):
        canvas_api_domain = request.body.get('custom_canvas_api_domain')
        canvas = canvas_api_domain and Canvas.find_by_domain(canvas_api_domain=canvas_api_domain)
        return canvas and canvas.lti_key == client_key

    @property
    def client_key_length(self):
        return 20, 32

    @property
    def nonce_length(self):
        return 20, 50

    def validate_timestamp_and_nonce(
            self,
            client_key,
            timestamp,
            nonce,
            request,
            request_token=None,
            access_token=None,
    ):
        # TODO: RequestValidator requires that this subclass implement this method. For now, we skip this validation.
        return True


def get_tool_metadata(host, tool_id):
    is_asset_library = tool_id == TOOL_ID_ASSET_LIBRARY
    api_path = '/api/auth/lti_launch/asset_library' if is_asset_library else '/api/auth/lti_launch/engagement_index'
    launch_url = f"https://{host.rstrip('/')}{api_path}"
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
        TOOL_ID_WHITEBOARDS: {
            'description': """
            The Whiteboards Tool allows for students to collaboratively work on whiteboards.
            Whiteboards can be used to remix assets from the Asset Library, create mind-maps, provide feedback, etc.
        """,
            'launch_url': launch_url,
            'title': 'Whiteboards',
        },
    }.get(tool_id, None)
