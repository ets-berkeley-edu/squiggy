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
from random import randint
from uuid import uuid4

from moto import mock_s3
from squiggy import std_commit
from squiggy.lib.util import is_admin, is_student, is_teaching
from squiggy.models.activity import Activity
from squiggy.models.asset import Asset
from squiggy.models.course import Course
from tests.util import mock_s3_bucket


def _api_get_whiteboard(client, whiteboard_id, expected_status_code=200):
    response = client.get(f'/api/whiteboard/{whiteboard_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestUpsertWhiteboardElement:

    @classmethod
    def _api_upsert_whiteboard_element(
            cls,
            client,
            whiteboard_elements,
            whiteboard_id,
            expected_status_code=200,
    ):
        params = {
            'socketId': _get_mock_socket_id(),
            'whiteboardElements': whiteboard_elements,
            'whiteboardId': whiteboard_id,
        }
        response = client.post(
            '/api/whiteboard_elements/upsert',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous_create(self, client, mock_whiteboard):
        """Denies anonymous user."""
        self._api_upsert_whiteboard_element(
            client=client,
            expected_status_code=401,
            whiteboard_elements=[_mock_whiteboard_element()],
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_unauthorized_create(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        user_id = _get_non_collaborator_user_id(mock_whiteboard)
        fake_auth.login(user_id)
        self._api_upsert_whiteboard_element(
            client=client,
            expected_status_code=401,
            whiteboard_elements=[_mock_whiteboard_element()],
            whiteboard_id=mock_whiteboard['id'],
        )

    @mock_s3
    def test_authorized_create(self, app, client, fake_auth, mock_whiteboard):
        """Authorized creates whiteboard elements."""
        mock_whiteboard_element = _mock_whiteboard_element()
        asset_id = mock_whiteboard_element['assetId']
        uuid = mock_whiteboard_element['uuid']
        asset = Asset.find_by_id(asset_id)

        with mock_s3_bucket(app):
            user_id = _get_authorized_user_id(mock_whiteboard)
            fake_auth.login(user_id)
            whiteboard_id = mock_whiteboard['id']
            self._api_upsert_whiteboard_element(
                client=client,
                whiteboard_elements=[mock_whiteboard_element],
                whiteboard_id=whiteboard_id,
            )
            api_json = _api_get_whiteboard(client, whiteboard_id)
            whiteboard_element = next((e for e in api_json['whiteboardElements'] if e['uuid'] == uuid), None)
            assert whiteboard_element
            assert whiteboard_element['assetId'] == asset.id
            assert whiteboard_element['element']['fill'] == whiteboard_element['element']['fill']
            assert whiteboard_element['element']['fontSize'] == whiteboard_element['element']['fontSize']
            assert whiteboard_element['element']['type'] == whiteboard_element['element']['type']

            activities = Activity.find_by_object_id(object_type='whiteboard', object_id=whiteboard_id)
            add_asset_activities = list(filter(lambda a: a.activity_type == 'whiteboard_add_asset', activities))
            assert len(add_asset_activities) == 1
            assert add_asset_activities[0].user_id == user_id

            get_add_asset_activities = list(filter(lambda a: a.activity_type == 'get_whiteboard_add_asset', activities))
            assert len(get_add_asset_activities) == 1
            assert get_add_asset_activities[0].user_id in [user.id for user in asset.users]

    def test_anonymous_update(self, client, mock_whiteboard):
        """Denies anonymous user."""
        self._api_upsert_whiteboard_element(
            client=client,
            expected_status_code=401,
            whiteboard_elements=mock_whiteboard['whiteboardElements'],
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_unauthorized_update(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        fake_auth.login(_get_non_collaborator_user_id(mock_whiteboard))
        self._api_upsert_whiteboard_element(
            client=client,
            expected_status_code=401,
            whiteboard_elements=mock_whiteboard['whiteboardElements'],
            whiteboard_id=mock_whiteboard['id'],
        )

    @mock_s3
    def test_authorized_update(self, app, client, fake_auth, mock_whiteboard):
        """Authorized user can update whiteboard elements."""
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        whiteboard_element = whiteboard_elements[-1]
        updated_fill = 'rgb(128,255,128)'
        whiteboard_element['element']['fill'] = updated_fill

        with mock_s3_bucket(app):
            fake_auth.login(_get_authorized_user_id(mock_whiteboard))
            whiteboard_id = mock_whiteboard['id']
            self._api_upsert_whiteboard_element(
                client=client,
                whiteboard_elements=mock_whiteboard['whiteboardElements'],
                whiteboard_id=whiteboard_id,
            )
            std_commit(allow_test_environment=True)

            api_json = _api_get_whiteboard(client, whiteboard_id)
            results = api_json['whiteboardElements']
            assert len(results) == len(whiteboard_elements)
            updated_whiteboard_element = next((result for result in results if result['id'] == whiteboard_element['id']), None)
            assert updated_whiteboard_element
            assert updated_whiteboard_element['element']['fill'] == updated_fill


class TestDeleteWhiteboardElements:

    @classmethod
    def _api_delete_whiteboard_elements(
            cls,
            client,
            uuids,
            whiteboard_id,
            expected_status_code=200,
    ):
        params = {
            'socketId': _get_mock_socket_id(),
            'uuids': uuids,
            'whiteboardId': whiteboard_id,
        }
        response = client.delete(
            '/api/whiteboard_elements/delete',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        uuids = [mock_whiteboard['whiteboardElements'][0]['uuid']]
        self._api_delete_whiteboard_elements(
            client=client,
            expected_status_code=401,
            uuids=uuids,
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        user_id = _get_non_collaborator_user_id(mock_whiteboard)
        fake_auth.login(user_id)
        uuids = [mock_whiteboard['whiteboardElements'][0]['uuid']]
        self._api_delete_whiteboard_elements(
            client=client,
            expected_status_code=401,
            uuids=uuids,
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_authorized(self, client, fake_auth, mock_whiteboard):
        """Authorized user can delete whiteboard elements."""
        user_id = _get_authorized_user_id(mock_whiteboard)
        fake_auth.login(user_id)

        whiteboard_id = mock_whiteboard['id']
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        count = len(whiteboard_elements)
        uuids = [whiteboard_elements[-1]['uuid'], whiteboard_elements[0]['uuid']]
        self._api_delete_whiteboard_elements(
            client=client,
            uuids=uuids,
            whiteboard_id=whiteboard_id,
        )
        api_json = _api_get_whiteboard(client, whiteboard_id)
        whiteboard_elements = api_json['whiteboardElements']
        assert len(whiteboard_elements) == count - 2
        for uuid in [w['uuid'] for w in whiteboard_elements]:
            assert uuid not in uuids


class TestOrderWhiteboardElements:

    @classmethod
    def _api_order_whiteboard_elements(
            cls,
            client,
            direction,
            uuids,
            whiteboard_id,
            expected_status_code=200,
    ):
        params = {
            'direction': direction,
            'socketId': _get_mock_socket_id(),
            'uuids': uuids,
            'whiteboardId': whiteboard_id,
        }
        response = client.post(
            '/api/whiteboard_elements/order',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_whiteboard):
        """Denies anonymous user."""
        uuids = [mock_whiteboard['whiteboardElements'][0]['uuid']]
        self._api_order_whiteboard_elements(
            client=client,
            direction='bringToFront',
            expected_status_code=401,
            uuids=uuids,
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_unauthorized(self, client, fake_auth, mock_whiteboard):
        """Denies unauthorized user."""
        user_id = _get_non_collaborator_user_id(mock_whiteboard)
        fake_auth.login(user_id)
        uuids = [mock_whiteboard['whiteboardElements'][0]['uuid']]
        self._api_order_whiteboard_elements(
            client=client,
            direction='bringToFront',
            expected_status_code=401,
            uuids=uuids,
            whiteboard_id=mock_whiteboard['id'],
        )

    def test_bring_element_to_front(self, client, fake_auth, mock_whiteboard):
        """Authorized user can 'bringToFront' a single whiteboard element."""
        self._verify_whiteboard_element_order(
            client=client,
            direction='bringToFront',
            fake_auth=fake_auth,
            selected_uuids=[mock_whiteboard['whiteboardElements'][1]['uuid']],
            whiteboard=mock_whiteboard,
        )

    def test_bring_elements_to_front(self, client, fake_auth, mock_whiteboard):
        """Authorized user can 'bringToFront' multiple whiteboard elements."""
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        whiteboard_elements = sorted(whiteboard_elements, key=lambda w: w['zIndex'])
        selected_uuids = [w['uuid'] for w in filter(lambda w: w['zIndex'] in [0, 2], whiteboard_elements)]
        assert len(selected_uuids) == 2
        self._verify_whiteboard_element_order(
            client=client,
            direction='bringToFront',
            fake_auth=fake_auth,
            selected_uuids=selected_uuids,
            whiteboard=mock_whiteboard,
        )

    def test_send_element_to_back(self, client, fake_auth, mock_whiteboard):
        """Authorized user can 'bringToFront' a single whiteboard element."""
        self._verify_whiteboard_element_order(
            client=client,
            direction='sendToBack',
            fake_auth=fake_auth,
            selected_uuids=[mock_whiteboard['whiteboardElements'][1]['uuid']],
            whiteboard=mock_whiteboard,
        )

    def test_send_elements_to_back(self, app, client, fake_auth, mock_whiteboard):
        """Authorized user can 'sendToBack' multiple whiteboard elements."""
        whiteboard_elements = mock_whiteboard['whiteboardElements']
        whiteboard_elements = sorted(whiteboard_elements, key=lambda w: w['zIndex'])
        selected_uuids = [w['uuid'] for w in filter(lambda w: w['zIndex'] in [1, 2], whiteboard_elements)]
        assert len(selected_uuids) == 2
        self._verify_whiteboard_element_order(
            client=client,
            direction='sendToBack',
            fake_auth=fake_auth,
            selected_uuids=selected_uuids,
            whiteboard=mock_whiteboard,
        )

    def _verify_whiteboard_element_order(
            self,
            client,
            direction,
            fake_auth,
            selected_uuids,
            whiteboard,
    ):
        user_id = _get_authorized_user_id(whiteboard)
        fake_auth.login(user_id)
        whiteboard_id = whiteboard['id']
        # Cherry-pick UUIDs for the re-order operation.
        whiteboard_elements = whiteboard['whiteboardElements']
        whiteboard_elements = sorted(whiteboard_elements, key=lambda w: w['zIndex'])
        other_uuids = [w['uuid'] for w in filter(lambda w: w['uuid'] not in selected_uuids, whiteboard_elements)]

        self._api_order_whiteboard_elements(
            client=client,
            direction=direction,
            uuids=selected_uuids,
            whiteboard_id=whiteboard_id,
        )
        api_json = _api_get_whiteboard(client, whiteboard_id)
        # Verify that the /whiteboard/:id API is returning ordered elements.
        whiteboard_elements = api_json['whiteboardElements']
        uuids = [w['uuid'] for w in whiteboard_elements]
        uuids_sorted = [w['uuid'] for w in sorted(whiteboard_elements, key=lambda w: w['zIndex'])]
        assert uuids == uuids_sorted
        # Verify
        if direction == 'bringToFront':
            assert uuids == (other_uuids + selected_uuids)
        elif direction == 'sendToBack':
            assert uuids == (selected_uuids + other_uuids)


def _get_authorized_user_id(whiteboard):
    student = next((u for u in whiteboard['users'] if is_student(u) and u['canvasEnrollmentState'] == 'active'), None)
    assert student
    return student['id']


def _get_mock_socket_id():
    return str(randint(1, 9999999))


def _get_non_collaborator_user_id(whiteboard):
    whiteboard_user_ids = [u['id'] for u in whiteboard['users']]
    course_id = whiteboard['courseId']

    def _is_unauthorized(user):
        return not is_admin(user) \
            and not is_teaching(user) \
            and user.canvas_enrollment_state == 'active' \
            and user.id not in whiteboard_user_ids
    unauthorized_users = list(filter(lambda u: _is_unauthorized(u), Course.find_by_id(course_id).users))
    user = unauthorized_users[0]
    return user.id


def _mock_whiteboard_element():
    uuid = str(uuid4())
    return {
        'assetId': 1,
        'element': {
            'fill': 'rgb(0,0,0)',
            'fontSize': 14,
            'text': '',
            'type': 'text',
            'uuid': uuid,
        },
        'uuid': uuid,
    }
