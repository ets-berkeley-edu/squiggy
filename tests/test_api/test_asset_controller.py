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

unauthorized_user_id = '666'


class TestGetAssets:
    """Assets API."""

    @classmethod
    def _api_get_assets(
            cls,
            client,
            asset_type=None,
            category_id=None,
            expected_status_code=200,
            has_comments=None,
            has_likes=None,
            has_views=None,
            keywords=None,
            limit=None,
            offset=None,
            order_by=None,
            section_id=None,
            user_id=None,
    ):
        params = {
            'assetType': asset_type,
            'categoryId': category_id,
            'hasComments': has_comments,
            'hasLikes': has_likes,
            'hasViews': has_views,
            'keywords': keywords,
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
            'sectionId': section_id,
            'userId': user_id,
        }
        response = client.post(
            '/api/assets',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_get_assets(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_get_assets(client, expected_status_code=401)

    def test_admin(self, client, fake_auth, authorized_user_id):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
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
            'categoryId': category and category.id,
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
        fake_auth.login(unauthorized_user_id)
        self._api_create_asset(client, expected_status_code=401)

    def test_create_asset(self, client, fake_auth, authorized_user_id):
        """Authorized user can create an asset."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_asset(client)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 0

    def test_create_asset_with_category(self, client, fake_auth, mock_category, authorized_user_id):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_asset(client, category=mock_category)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 1
        assert categories[0]['id'] == mock_category.id
        assert categories[0]['title'] == mock_category.title


class TestUpdateAsset:
    """Update asset API."""

    @staticmethod
    def _api_update_asset(client, asset, expected_status_code=200):
        params = {
            'assetId': asset.id,
            'categoryId': asset.categories[0].id if len(asset.categories) else None,
            'description': asset.description,
            'title': asset.title,
        }
        response = client.post(
            '/api/asset/update',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_asset):
        """Denies anonymous user."""
        self._api_update_asset(client, asset=mock_asset, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_asset):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_update_asset(client, asset=mock_asset, expected_status_code=401)

    def test_update_asset(self, authorized_user_id, client, fake_auth, mock_asset, mock_category):
        """Authorized user can update asset."""
        fake_auth.login(authorized_user_id)
        mock_asset.title = "'I'll be your mirror'"
        mock_asset.description = "'Reflect what you are, in case you don't know'"
        mock_asset.categories = [mock_category]
        api_json = self._api_update_asset(client, asset=mock_asset)
        assert api_json['id'] == mock_asset.id
        assert len(api_json['categories']) == 1
        assert api_json['categories'][0]['id'] == mock_category.id
        assert api_json['description'] == mock_asset.description
        assert api_json['title'] == mock_asset.title
