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

admin_uid = '2040'
unauthorized_uid = '1015674'


class TestGetAssets:
    """Assets API."""

    @classmethod
    def _api_get_assets(cls, client, course_site_id=1502870, domain='bcourses.berkeley.edu', expected_status_code=200):
        response = client.get(f'/api/{domain}/{course_site_id}/assets')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_assets(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_uid)
        self._api_get_assets(client, expected_status_code=401)

    def test_admin(self, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(admin_uid)
        api_json = self._api_get_assets(client)
        assert 'total' in api_json
        assert 'results' in api_json


class TestCreateAsset:
    """Create asset API."""

    @staticmethod
    def _api_create_asset(
            client,
            asset_type='link',
            category=None,
            description='Baby, be good, do what you should. You know it will be alright',
            title='What goes on in your mind?',
            url='https://www.youtube.com/watch?v=Pxq63cYIY1c',
            expected_status_code=200,
    ):
        params = {
            'categoryIds': category and [category.id],
            'description': description,
            'title': title,
            'type': asset_type,
            'url': url,
        }
        response = client.post(
            '/api/asset/create',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_asset(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_uid)
        self._api_create_asset(client, expected_status_code=401)

    def test_create_asset(self, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(admin_uid)
        api_json = self._api_create_asset(client)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 0

    def test_create_asset_with_category(self, client, fake_auth, mock_category):
        """Returns a well-formed response."""
        fake_auth.login(admin_uid)
        api_json = self._api_create_asset(client, category=mock_category)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 1
        assert categories[0]['id'] == mock_category.id
        assert categories[0]['title'] == mock_category.title
