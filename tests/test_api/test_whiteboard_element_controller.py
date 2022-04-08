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
from uuid import uuid4

from squiggy import std_commit
from squiggy.lib.util import is_admin, is_teaching
from squiggy.models.course import Course


class TestCreateWhiteboardElement:

    @staticmethod
    def _api_create_whiteboard_elements(client, whiteboard_elements, whiteboard_id, expected_status_code=200):
        response = client.post(
            '/api/whiteboard/elements/create',
            data=json.dumps({
                'socketId': str(uuid4()),
                'whiteboardElements': whiteboard_elements,
                'whiteboardId': whiteboard_id,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        # Anonymous
        self._api_create_whiteboard_elements(
            client=client,
            expected_status_code=401,
            whiteboard_elements=_mock_whiteboard_elements(),
            whiteboard_id=mock_whiteboard['id'],
        )
        # Unauthorized
        fake_auth.login(_get_unauthorized_user_id(mock_whiteboard))
        self._api_create_whiteboard_elements(
            client=client,
            expected_status_code=400,
            whiteboard_elements=_mock_whiteboard_elements(),
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_authorized(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        fake_auth.login(_get_authorized_user_id(mock_whiteboard))
        whiteboard_elements = _mock_whiteboard_elements()

        api_json = self._api_create_whiteboard_elements(
            client=client,
            whiteboard_elements=whiteboard_elements,
            whiteboard_id=mock_whiteboard['id'],
        )
        assert len(api_json) == len(whiteboard_elements)


class TestUpdateWhiteboardElements:

    @staticmethod
    def _api_update_whiteboard_elements(client, whiteboard_elements, whiteboard_id, expected_status_code=200):
        response = client.post(
            '/api/whiteboard/elements/update',
            data=json.dumps({
                'socketId': str(uuid4()),
                'whiteboardElements': whiteboard_elements,
                'whiteboardId': whiteboard_id,
            }),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        # Anonymous
        self._api_update_whiteboard_elements(
            client=client,
            whiteboard_elements=mock_whiteboard['whiteboardElements'],
            expected_status_code=401,
            whiteboard_id=mock_whiteboard['id'],
        )
        fake_auth.login(_get_unauthorized_user_id(mock_whiteboard))
        self._api_update_whiteboard_elements(
            client=client,
            whiteboard_elements=mock_whiteboard['whiteboardElements'],
            expected_status_code=400,
            whiteboard_id=1,
        )

    def test_authorized(self, client, fake_auth, mock_whiteboard):
        """Authorized user can update whiteboard elements."""
        fake_auth.login(_get_authorized_user_id(mock_whiteboard))
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        whiteboard_element = whiteboard_elements[-1]
        updated_fill = 'rgb(128,255,128)'
        whiteboard_element['element']['fill'] = updated_fill
        api_json = self._api_update_whiteboard_elements(
            client=client,
            whiteboard_elements=whiteboard_elements,
            whiteboard_id=mock_whiteboard['id'],
        )
        std_commit(allow_test_environment=True)
        assert len(api_json) and len(api_json) == len(whiteboard_elements)
        updated_whiteboard_element = next((e for e in api_json if e['id'] == whiteboard_element['id']), None)
        assert updated_whiteboard_element
        assert updated_whiteboard_element['element']['fill'] == updated_fill


def _api_get_whiteboard(whiteboard_id, client, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


def _get_authorized_user_id(whiteboard):
    course_id = whiteboard['courseId']
    instructors = list(filter(lambda u: is_teaching(u), Course.find_by_id(course_id).users))
    return instructors[0].id


def _get_unauthorized_user_id(whiteboard):
    course_id = whiteboard['courseId']
    instructors = list(filter(lambda u: not is_admin(u) and not is_teaching(u), Course.find_by_id(course_id).users))
    return instructors[0].id


def _mock_whiteboard_elements():
    return [
        {
            'assetId': 1,
            'element': {
                'fill': 'rgb(0,0,0)',
                'fontSize': 14,
                'text': '',
                'type': 'text',
            },
        },
        {
            'assetId': 2,
            'element': {
                'fill': 'rgb(0,0,0)',
                'shape': 'Rect:thin',
                'type': 'shape',
            },
        },
    ]
