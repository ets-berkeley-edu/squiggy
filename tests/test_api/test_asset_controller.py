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
import os

from moto import mock_s3
from squiggy import std_commit
from squiggy.lib.util import is_teaching
from squiggy.models.course import Course
from tests.util import mock_s3_bucket

unauthorized_user_id = '666'


class TestGetAsset:
    """Asset API."""

    @staticmethod
    def _api_asset(asset_id, client, expected_status_code=200):
        response = client.get(f'/api/asset/{asset_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client, mock_asset):
        """Denies anonymous user."""
        self._api_asset(asset_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_asset):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_asset(asset_id=1, client=client, expected_status_code=401)

    def test_owner_view_asset(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can view asset."""
        fake_auth.login(mock_asset.users[0].id)
        asset = self._api_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id

    def test_teacher_view_asset(self, client, fake_auth, mock_asset):
        """Authorized user can view asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = self._api_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id


class TestDownloadAsset:
    """Download Asset API."""

    @staticmethod
    def _api_download_asset(app, asset_id, client, expected_status_code=200):
        response = client.get(f'/api/asset/{asset_id}/download')
        assert response.status_code == expected_status_code
        return response.json

    @mock_s3
    def test_anonymous(self, app, client, mock_asset):
        """Denies anonymous user."""
        self._api_download_asset(app, asset_id=1, client=client, expected_status_code=401)

    @mock_s3
    def test_unauthorized(self, app, client, fake_auth, mock_asset):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_download_asset(app, asset_id=1, client=client, expected_status_code=401)

    @mock_s3
    def test_owner_download_asset(self, app, client, fake_auth, mock_asset, mock_category):
        """Authorized user can download asset."""
        fake_auth.login(mock_asset.users[0].id)
        # TODO: Mock S3 so authorized user actually gets download. For now, 404 oddly indicates success.
        self._api_download_asset(app, asset_id=mock_asset.id, client=client, expected_status_code=404)

    @mock_s3
    def test_teacher_download(self, app, client, fake_auth, mock_asset):
        """Authorized user can download asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        # TODO: Mock S3 so authorized user actually gets download. For now, 404 oddly indicates success.
        self._api_download_asset(app, asset_id=mock_asset.id, client=client, expected_status_code=404)


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
    def _api_create_link_asset(
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

    @staticmethod
    def _api_create_file_asset(
            client,
            asset_type='file',
            category=None,
            description='Gone to choose, choose again',
            title='The Black Angel\'s Death Song',
            expected_status_code=200,
    ):
        params = {
            'description': description,
            'title': title,
            'type': asset_type,
        }
        if category and category.id:
            params['categoryId'] = category.id
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        params['file[0]'] = open(f'{base_dir}/fixtures/mock_file_upload/the_gift.txt', 'rb')
        response = client.post(
            '/api/asset/create',
            data=params,
            content_type='multipart/form-data',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_link_asset(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_create_link_asset(client, expected_status_code=401)

    def test_create_link_asset(self, client, fake_auth, authorized_user_id):
        """Authorized user can create an asset."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_link_asset(client)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 0

    def test_create_link_asset_with_category(self, client, fake_auth, mock_category, authorized_user_id):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_link_asset(client, category=mock_category)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 1
        assert categories[0]['id'] == mock_category.id
        assert categories[0]['title'] == mock_category.title

    @mock_s3
    def test_create_file_asset(self, client, app, fake_auth, authorized_user_id):
        """Authorized user can create an asset."""
        fake_auth.login(authorized_user_id)
        with mock_s3_bucket(app):
            api_json = self._api_create_file_asset(client)
            assert 'id' in api_json
            assert api_json['title'] == 'The Black Angel\'s Death Song'
            categories = api_json['categories']
            assert len(categories) == 0


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

    def test_update_asset_by_owner(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can update asset."""
        fake_auth.login(mock_asset.users[0].id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_update_asset_by_teacher(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can update asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def _verify_update_asset(self, client, mock_asset, mock_category):
        mock_asset.title = "'I'll be your mirror'"
        mock_asset.description = "'Reflect what you are, in case you don't know'"
        mock_asset.categories = [mock_category]
        api_json = self._api_update_asset(client, asset=mock_asset)
        assert api_json['id'] == mock_asset.id
        assert len(api_json['categories']) == 1
        assert api_json['categories'][0]['id'] == mock_category.id
        assert api_json['description'] == mock_asset.description
        assert api_json['title'] == mock_asset.title


class TestDeleteAsset:
    """Delete asset API."""

    @staticmethod
    def _api_delete_asset(asset_id, client, expected_status_code=200):
        response = client.delete(f'/api/asset/{asset_id}/delete')
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_delete_asset(asset_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_delete_asset(asset_id=1, client=client, expected_status_code=401)

    def test_delete_asset_by_owner(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can delete asset."""
        fake_auth.login(mock_asset.users[0].id)
        self._verify_delete_asset(mock_asset.id, client)

    def test_delete_asset_by_teacher(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can delete asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        self._verify_delete_asset(mock_asset.id, client)

    def _verify_delete_asset(self, asset_id, client):
        self._api_delete_asset(asset_id=asset_id, client=client)
        std_commit(allow_test_environment=True)
        response = client.get(f'/api/asset/{asset_id}')
        assert response.status_code == 404
