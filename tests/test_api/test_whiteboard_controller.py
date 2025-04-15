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

import json

from squiggy.lib.util import is_teaching
from squiggy.models.course import Course

unauthorized_user_id = '666'


def _api_get_whiteboard(client, whiteboard_id, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetWhiteboard:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_whiteboard(client=client, expected_status_code=401, whiteboard_id=1)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_whiteboard(client=client, expected_status_code=401, whiteboard_id=1)

    def test_owner_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Authorized user can view whiteboard."""
        fake_auth.login(mock_whiteboard['users'][0]['id'])
        asset = _api_get_whiteboard(client=client, whiteboard_id=mock_whiteboard['id'])
        assert asset['id'] == mock_whiteboard['id']

    def test_teacher_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Teacher can view whiteboard."""
        course = Course.find_by_canvas_course_id(
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=1502870,
        )
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard['id'], client=client)
        assert asset['id'] == mock_whiteboard['id']

    def test_student_view_whiteboard(self, client, fake_auth, mock_whiteboard):
        """Collaborator can view whiteboard created by student in other section."""
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            asset = _api_get_whiteboard(whiteboard_id=mock_whiteboard['id'], client=client)
            assert asset['id'] == mock_whiteboard['id']


class TestGetWhiteboards:

    @classmethod
    def _api_get_whiteboards(
            cls,
            client,
            expected_status_code=200,
            include_deleted=False,
            limit=None,
            offset=None,
            order_by=None,
    ):
        params = {
            'includeDeleted': include_deleted,
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
        }
        response = client.post(
            '/api/whiteboards',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_whiteboards(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_whiteboards(client, expected_status_code=401)

    def test_view_whiteboard_protected_per_section(self, client, fake_auth, mock_whiteboard, mock_whiteboard_course):
        """Student in an asset-siloed course cannot view whiteboard created by student in other section."""
        mock_whiteboard_course.protects_assets_per_section = True
        collaborators = mock_whiteboard['users']
        assert collaborators[0]['canvasCourseSections'] != collaborators[1]['canvasCourseSections']
        for collaborator in collaborators:
            fake_auth.login(collaborator['id'])
            api_json = self._api_get_whiteboards(
                client=client,
                order_by='collaborator',
            )
            expected_count = 1 if collaborator['id'] == mock_whiteboard['createdBy'] else 0
            whiteboards = api_json['results']
            assert len(whiteboards) == api_json['total']
            assert len(whiteboards) == expected_count


def _get_sample_user(canvas_course_role, course):
    return next((u for u in course.users if u.canvas_course_role == canvas_course_role), None)
