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

import json

from squiggy.models.activity_type import DEFAULT_ACTIVITY_TYPE_CONFIGURATION
from squiggy.models.user import User


def api_get_configuration(client, expected_status_code=200):
    response = client.get('/api/activities/configuration')
    assert response.status_code == expected_status_code
    return response.json


def api_update_configuration(client, updates=None, expected_status_code=200):
    response = client.post(
        '/api/activities/configuration',
        data=json.dumps(updates),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code


class TestGetActivityConfiguration:
    """API to get activity configuration for a course."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        api_get_configuration(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        api_get_configuration(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth):
        """Default configuration values with db-based overrides are returned to authorized user."""
        teacher = User.find_by_canvas_user_id(9876543)
        fake_auth.login(teacher.id)
        response = api_get_configuration(client)
        assert len(response) == len(DEFAULT_ACTIVITY_TYPE_CONFIGURATION)
        for config in response:
            default_config = next(c for c in DEFAULT_ACTIVITY_TYPE_CONFIGURATION if c['type'] == config['type'])
            if config['type'] == 'asset_add':
                assert config['points'] == 5
                assert config['enabled'] is True
            elif config['type'] == 'asset_comment':
                assert config['points'] == 2
                assert config['enabled'] is True
            else:
                assert config['points'] == default_config['points']
                assert config['enabled'] == default_config['enabled']


class TestUpdateActivityConfiguration:
    """API to ipdate activity configuration for a course."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        api_update_configuration(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        api_update_configuration(client, expected_status_code=401)

    def test_ill_formed_data(self, client, fake_auth):
        """Rejects ill-formed configurations."""
        teacher = User.find_by_canvas_user_id(9876543)
        fake_auth.login(teacher.id)
        api_update_configuration(
            client,
            updates=[
                {'type': 'asset_add', 'enabled': True, 'points': 5},
                {'type': 'asset_puree', 'enabled': False, 'points': 4000},
            ],
            expected_status_code=400,
        )

    def test_well_formed_data(self, client, fake_auth):
        teacher = User.find_by_canvas_user_id(9876543)
        fake_auth.login(teacher.id)
        api_update_configuration(
            client,
            updates=[
                {'type': 'asset_add', 'enabled': False, 'points': 3},
                {'type': 'get_asset_comment', 'enabled': True, 'points': 12},
            ],
        )
        new_config = api_get_configuration(client)
        assert len(new_config) == len(DEFAULT_ACTIVITY_TYPE_CONFIGURATION)
        for config in new_config:
            default_config = next(c for c in DEFAULT_ACTIVITY_TYPE_CONFIGURATION if c['type'] == config['type'])
            if config['type'] == 'asset_add':
                assert config['points'] == 3
                assert config['enabled'] is False
            elif config['type'] == 'asset_comment':
                assert config['points'] == 2
                assert config['enabled'] is True
            elif config['type'] == 'get_asset_comment':
                assert config['points'] == 12
                assert config['enabled'] is True
            else:
                assert config['points'] == default_config['points']
                assert config['enabled'] == default_config['enabled']
