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

from squiggy.models.user import User

unauthorized_user_id = '666'


class TestCreateCategory:
    """Create category API."""

    @staticmethod
    def _api_create_category(client, title='What goes on in your mind?', expected_status_code=200):
        response = client.post(
            '/api/category/create',
            data=json.dumps({'title': title}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_category(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        student = User.find_by_canvas_user_id(8765432)
        fake_auth.login(student.id)
        self._api_create_category(client, expected_status_code=401)

    def test_create_category(self, client, fake_auth, authorized_user_id):
        """Authorized user can create an category."""
        fake_auth.login(authorized_user_id)
        title = 'Globe of Frogs'
        api_json = self._api_create_category(client=client, title=title)
        assert 'id' in api_json
        assert api_json['title'] == title


class TestGetCategories:
    """Categories API."""

    @classmethod
    def _api_get_categories(cls, client, expected_status_code=200, include_hidden=False):
        response = client.get(f'/api/categories?includeHidden={include_hidden}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_categories(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_categories(client, expected_status_code=401)

    def test_authorized(self, client, authorized_user_id, fake_auth, mock_asset):
        """Authorized user can get all categories."""
        fake_auth.login(mock_asset.users[0].id)
        categories_all = self._api_get_categories(client, include_hidden=True)
        categories_visible = self._api_get_categories(client, include_hidden=False)

        assert len(categories_all) > len(categories_visible)
        category = categories_visible[0]
        assert category.get('title')
        assert category.get('assetCount') > 0
