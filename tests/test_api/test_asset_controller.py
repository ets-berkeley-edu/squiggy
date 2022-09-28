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
import os
from random import randrange

from moto import mock_s3
import responses
from squiggy import std_commit
from squiggy.lib.util import is_student, is_teaching
from squiggy.models.activity import Activity
from squiggy.models.course import Course
from squiggy.models.user import User
from tests.util import mock_s3_bucket

unauthorized_user_id = '666'


def _api_get_asset(asset_id, client, expected_status_code=200):
    response = client.get(f'/api/asset/{asset_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestGetAsset:

    def test_anonymous(self, client, mock_asset):
        """Denies anonymous user."""
        _api_get_asset(asset_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_asset):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_asset(asset_id=1, client=client, expected_status_code=401)

    def test_owner_view_asset(self, client, fake_auth, mock_asset, mock_category):
        """Authorized user can view asset."""
        fake_auth.login(mock_asset.created_by)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id

    def test_teacher_view_asset(self, client, fake_auth, mock_asset):
        """Authorized user can view asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id

    def test_increment_asset_view_count(self, client, fake_auth, mock_asset):
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        # Instructor 1 increments view count.
        fake_auth.login(instructors[0].id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['views'] == 1
        # Instructor 2 increments view count.
        fake_auth.login(instructors[1].id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['views'] == 2
        # Repeat views increment,
        fake_auth.login(instructors[0].id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['views'] == 3
        # Views by asset owners do not increment.
        fake_auth.login(mock_asset.created_by)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['views'] == 3

    def test_view_protected_asset(self, client, fake_auth, mock_asset, mock_asset_course):
        """Student in an asset-siloed course cannot view asset created by student in other section."""
        course = mock_asset_course
        course.protects_assets_per_section = True

        section_a_student = User.query.filter_by(course_id=course.id, canvas_course_role='Student', canvas_course_sections=['section A']).first()
        fake_auth.login(section_a_student.id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id

        section_b_student = User.query.filter_by(course_id=course.id, canvas_course_role='Student', canvas_course_sections=['section B']).first()
        fake_auth.login(section_b_student.id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client, expected_status_code=404)


class TestDownloadAsset:

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
        fake_auth.login(mock_asset.created_by)
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

    @classmethod
    def _api_get_assets(
            cls,
            client,
            asset_type=None,
            category_id=None,
            expected_status_code=200,
            keywords=None,
            limit=20,
            offset=0,
            order_by=None,
            section_id=None,
            user_id=None,
    ):
        params = {
            'assetType': asset_type,
            'categoryId': category_id,
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

    def test_admin(self, authorized_user_id, client, fake_auth):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        api_json = self._api_get_assets(client)
        assert 'total' in api_json
        assert 'results' in api_json

    def test_assets_for_course(self, authorized_user_id, client, fake_auth):
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        api_json = self._api_get_assets(client)
        # Feed shape
        assert api_json['offset'] == 0
        assert api_json['total'] == len(api_json['results'])
        # Ordering
        assert api_json['results'][0]['id'] > api_json['results'][1]['id']
        # Asset structure
        for asset in api_json['results']:
            assert asset['body'] is None
            assert asset['canvasAssignmentId'] is None
            assert asset['commentCount'] == 0
            assert asset['courseId'] == user.course.id
            assert asset['createdAt'] is not None
            assert asset['deletedAt'] is None
            assert asset['description'] is None
            assert asset['imageUrl'] is None
            assert asset['liked'] is False
            assert asset['likes'] == 0
            assert asset['pdfUrl'] is None
            assert asset['previewMetadata'] == '{}'
            assert asset['previewStatus'] == 'pending'
            assert asset['thumbnailUrl'] is None
            assert asset['title'] is not None
            assert asset['type']
            assert asset['createdAt'] is not None
            assert asset['updatedAt'] is not None
            assert asset['views'] == 0
            assert asset['visible'] is True
            for key in ('downloadUrl', 'mime', 'source'):
                assert key in asset, f'{key} not present in asset JSON'

            assert len(asset['users']) == 1
            for key in ('id', 'canvasFullName', 'canvasUserId', 'canvasCourseRole', 'canvasEnrollmentState', 'canvasCourseSections', 'canvasImage'):
                assert key in asset['users'][0]

    def test_teacher_assets_protected_per_section(self, authorized_user_id, client, fake_auth, mock_asset_course):
        """Teacher in an asset-siloed course can see all assets for the course."""
        mock_asset_course.protects_assets_per_section = True
        # Instructor can see all assets for the course
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        api_json = self._api_get_assets(client)
        assert api_json['total'] > 2
        assert next(asset for asset in api_json['results'] if asset['users'][0]['canvasCourseSections'] == ['section A'])
        assert next(asset for asset in api_json['results'] if asset['users'][0]['canvasCourseSections'] == ['section B'])
        assert next(asset for asset in api_json['results'] if asset['users'][0]['canvasCourseRole'] != 'Student')

    def test_student_assets_protected_per_section(self, client, fake_auth, mock_asset_course):
        """Student in an asset-siloed course can see assets created by teacher or other student in their section."""
        mock_asset_course.protects_assets_per_section = True
        # Students can see the instructor's assets plus any other assets for their section
        for section in ('section A', 'section B'):
            student = User.query.filter_by(course_id=mock_asset_course.id, canvas_course_role='Student', canvas_course_sections=[section]).first()
            fake_auth.login(student.id)
            api_json = self._api_get_assets(client)
            assert api_json['total'] > 1
            for asset in api_json['results']:
                assert len(asset['users']) == 1
                assert asset['users'][0]['canvasCourseRole'] != 'Student' or asset['users'][0]['canvasCourseSections'] == [section]


class TestCreateAsset:

    @staticmethod
    def _api_create_link_asset(
            client,
            asset_type='link',
            category=None,
            description='Baby, be good, do what you should. You know it will be alright',
            expected_status_code=200,
            title='What goes on in your mind?',
            url='https://www.youtube.com/watch?v=Pxq63cYIY1c',
            visible=True,
    ):
        params = {
            'categoryId': category and category.id,
            'description': description,
            'title': title,
            'type': asset_type,
            'url': url,
            'visible': visible,
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
            bookmarklet=False,
            category=None,
            description='Gone to choose, choose again',
            title='The Black Angel\'s Death Song',
            url=None,
            expected_status_code=200,
    ):
        params = {
            'bookmarklet': bookmarklet,
            'description': description,
            'title': title,
            'type': asset_type,
            'url': url,
        }
        if category and category.id:
            params['categoryId'] = category.id
        if not bookmarklet:
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
        user_points = User.find_by_id(authorized_user_id).points
        api_json = self._api_create_link_asset(client, category=mock_category)
        assert 'id' in api_json
        assert api_json['title'] == 'What goes on in your mind?'
        categories = api_json['categories']
        assert len(categories) == 1
        assert categories[0]['id'] == mock_category.id
        assert categories[0]['title'] == mock_category.title
        assert User.find_by_id(authorized_user_id).points == user_points + 5

    @responses.activate
    def test_create_happy_jamboard(self, client, fake_auth, authorized_user_id):
        """Links to available Google Jamboards pass validation."""
        happy_jamboard_url = 'https://jamboard.google.com/5678'
        responses.add(
            responses.GET,
            happy_jamboard_url,
            body='<HTML><HEAD>Jam On!</HEAD></HTML>',
            status=200,
        )
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_link_asset(client, url=happy_jamboard_url)
        assert 'id' in api_json

    @responses.activate
    def test_create_sad_jamboard(self, client, fake_auth, authorized_user_id):
        """Links to restricted-access Google Jamboards fail validation."""
        sad_jamboard_url = 'https://jamboard.google.com/666'
        google_login_url = f'https://accounts.google.com/ServiceLogin?service=jamboardcore&continue={sad_jamboard_url}'
        responses.add(
            responses.GET,
            sad_jamboard_url,
            status=302,
            headers={'Location': google_login_url},
        )
        responses.add(
            responses.GET,
            google_login_url,
            status=200,
            body='<HTML><HEAD>Please identify 14 motorcycles to prove you are not a robot.</HEAD></HTML>',
        )
        fake_auth.login(authorized_user_id)
        api_json = self._api_create_link_asset(client, url=sad_jamboard_url, expected_status_code=400)
        assert api_json['message'] == 'In order to add a Google Jamboard to the Asset Library, sharing must be set to "Anyone with the link."'

    @mock_s3
    def test_create_file_asset(self, client, app, fake_auth, authorized_user_id):
        """Authorized user can create an asset."""
        fake_auth.login(authorized_user_id)
        user_points = User.find_by_id(authorized_user_id).points
        with mock_s3_bucket(app):
            api_json = self._api_create_file_asset(client)
            assert 'id' in api_json
            assert api_json['title'] == 'The Black Angel\'s Death Song'
            assert api_json['mime'] == 'text/plain'
            categories = api_json['categories']
            assert len(categories) == 0
        assert User.find_by_id(authorized_user_id).points == user_points + 5

    @mock_s3
    def test_bookmarklet_create_file_asset(self, client, app, fake_auth, authorized_user_id):
        """Authorized user can create an asset with the Bookmarklet."""
        fake_auth.login(authorized_user_id)
        user_points = User.find_by_id(authorized_user_id).points
        with mock_s3_bucket(app):
            filename = 'lenny_and_squiggy.ico'
            api_json = self._api_create_file_asset(
                client,
                bookmarklet=True,
                url=f'https://en.wikipedia.org/static/favicon/{filename}#anchor?ref=#?uestlove',
            )
            assert 'id' in api_json
            download_url = api_json['downloadUrl']
            assert download_url and download_url.endswith(f'-{filename}')
        assert User.find_by_id(authorized_user_id).points == user_points + 5

    def test_asset_creation_activity(self, authorized_user_id, client, fake_auth):
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        api_json = self._api_create_link_asset(
            client=client,
            title='Riding in a Stutz Bear Cat, Jim',
            url='https://genius.com/The-velvet-underground-sweet-jane-lyrics',
        )
        asset_id = api_json['id']
        activities = Activity.query.filter_by(asset_id=asset_id).all()
        assert len(activities) == 1
        assert activities[0].activity_type == 'asset_add'
        assert activities[0].course_id == user.course.id
        assert activities[0].object_type == 'asset'
        assert activities[0].object_id == asset_id
        assert activities[0].asset_id == asset_id
        assert activities[0].user_id == user.id

    def test_asset_creation_invisible_no_activities(self, authorized_user_id, client, fake_auth):
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        api_json = self._api_create_link_asset(
            client=client,
            title='Riding in a Stutz Bear Cat, Jim',
            url='https://genius.com/The-velvet-underground-sweet-jane-lyrics',
            visible=False,
        )
        activities = Activity.query.filter_by(asset_id=api_json['id']).all()
        assert len(activities) == 0


class TestUpdateAsset:

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
        """Asset owner can update asset."""
        fake_auth.login(mock_asset.created_by)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_update_asset_by_student(self, client, fake_auth, mock_asset, mock_category):
        """Student asset user in the same course as the owner can update asset."""
        course_users = Course.find_by_id(mock_asset.course_id).users
        user_iterator = (user for user in course_users if user.id != mock_asset.created_by and is_student(user))
        different_user = next(user_iterator)
        mock_asset.users = [mock_asset.users[0], different_user]
        std_commit(allow_test_environment=True)
        fake_auth.login(different_user.id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_update_asset_by_teacher(self, client, fake_auth, mock_asset, mock_category):
        """Teacher can update asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_teacher_update_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_category):
        """Teacher in an asset-siloed course can update asset."""
        mock_asset_course.protects_assets_per_section = True
        # Instructor can update asset
        instructors = list(filter(lambda u: is_teaching(u), mock_asset_course.users))
        fake_auth.login(instructors[0].id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_owner_update_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users, mock_category):
        """Asset owner in an asset-siloed course can update asset."""
        mock_asset_course.protects_assets_per_section = True
        asset_owner, same_section_student, different_section_student = mock_asset_users
        # Asset owner can update asset
        fake_auth.login(asset_owner.id)
        self._verify_update_asset(client, mock_asset, mock_category)

    def test_student_update_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users, mock_category):
        """Student in an asset-siloed course cannot update asset created by student in other section."""
        mock_asset_course.protects_assets_per_section = True
        asset_owner, same_section_student, different_section_student = mock_asset_users
        # Asset user in asset owner's section can update asset
        fake_auth.login(same_section_student.id)
        self._verify_update_asset(client, mock_asset, mock_category)
        # Asset user in a different section cannot update asset
        fake_auth.login(different_section_student.id)
        self._api_update_asset(client, asset=mock_asset, expected_status_code=400)

    def _verify_update_asset(self, client, mock_asset, mock_category):
        mock_asset.title = "I'll be your mirror"
        mock_asset.description = "Reflect what you are, in case you don't know"
        mock_asset.categories = [mock_category]
        api_json = self._api_update_asset(client, asset=mock_asset)
        assert api_json['id'] == mock_asset.id
        assert len(api_json['categories']) == 1
        assert api_json['categories'][0]['id'] == mock_category.id
        assert api_json['description'] == mock_asset.description
        assert api_json['title'] == mock_asset.title


class TestRefreshAssetPreview:

    @staticmethod
    def _api_refresh_asset_preview(asset_id, client, expected_status_code=200):
        response = client.post(f'/api/asset/{asset_id}/refresh_preview')
        assert response.status_code == expected_status_code

    def test_anonymous(self, client, mock_asset):
        """Denies anonymous user."""
        self._api_refresh_asset_preview(mock_asset.id, client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth, mock_asset):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_refresh_asset_preview(mock_asset.id, client, expected_status_code=401)

    def test_refresh_asset_by_owner(self, client, db_session, fake_auth, mock_asset):
        """Asset owner can refresh asset preview."""
        mock_asset.preview_status = 'done'
        fake_auth.login(mock_asset.created_by)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'

    def test_refresh_asset_by_student(self, client, fake_auth, mock_asset, mock_asset_users, mock_category):
        """Student asset user in the same course as the owner can refresh asset preview."""
        asset_owner, same_section_student, different_section_student = mock_asset_users
        # Asset user in asset owner's section can refresh asset
        mock_asset.preview_status = 'done'
        fake_auth.login(same_section_student.id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'
        # Asset user in a different section can refresh asset
        mock_asset.preview_status = 'done'
        fake_auth.login(different_section_student.id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'

    def test_refresh_asset_by_instructor(self, client, db_session, fake_auth, mock_asset):
        """Instructor can refresh asset preview."""
        mock_asset.preview_status = 'done'
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'

    def test_teacher_refresh_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course):
        """Instructor in an asset-siloed course can refresh asset preview."""
        mock_asset_course.protects_assets_per_section = True
        mock_asset.preview_status = 'done'
        instructors = list(filter(lambda u: is_teaching(u), mock_asset_course.users))
        fake_auth.login(instructors[0].id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'

    def test_owner_update_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users):
        """Asset owner in an asset-siloed course can refresh asset preview."""
        asset_owner, same_section_student, different_section_student = mock_asset_users
        mock_asset_course.protects_assets_per_section = True
        mock_asset.preview_status = 'done'
        fake_auth.login(asset_owner.id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'

    def test_student_update_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users):
        """Student in an asset-siloed course cannot refresh asset created by student in other section."""
        asset_owner, same_section_student, different_section_student = mock_asset_users
        mock_asset_course.protects_assets_per_section = True
        # Asset user in asset owner's section can refresh asset
        mock_asset.preview_status = 'done'
        fake_auth.login(same_section_student.id)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'done'
        self._api_refresh_asset_preview(mock_asset.id, client)
        api_json = _api_get_asset(mock_asset.id, client)
        assert api_json['previewStatus'] == 'pending'
        # Asset user in a different section cannot refresh asset
        fake_auth.login(different_section_student.id)
        self._api_refresh_asset_preview(mock_asset.id, client, expected_status_code=400)


class TestDeleteAsset:

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

    def test_delete_asset_by_owner_without_engagement(self, client, fake_auth, mock_asset, mock_category):
        """Asset deletion by owner is allowed if the asset has no comments or likes."""
        mock_asset.likes = 0
        mock_asset.comment_count = 0
        fake_auth.login(mock_asset.created_by)
        self._verify_delete_asset(mock_asset.id, client)

    def test_delete_asset_by_owner_with_engagement(self, client, fake_auth, mock_asset, mock_category):
        """Asset deletion by owner is forbidden once the asset has comments or likes."""
        fake_auth.login(mock_asset.created_by)
        self._api_delete_asset(mock_asset.id, client, expected_status_code=400)

    def test_delete_asset_by_teacher(self, client, fake_auth, mock_asset, mock_category):
        """Teacher can delete asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        self._verify_delete_asset(mock_asset.id, client)

    def test_owner_delete_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course):
        """Asset owner in an asset-siloed course can delete asset."""
        mock_asset_course.protects_assets_per_section = True
        mock_asset.likes = 0
        mock_asset.comment_count = 0
        fake_auth.login(mock_asset.created_by)
        self._verify_delete_asset(mock_asset.id, client)

    def test_teacher_delete_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course):
        """Teacher in an asset-siloed course can delete asset."""
        mock_asset_course.protects_assets_per_section = True
        instructors = list(filter(lambda u: is_teaching(u), mock_asset_course.users))
        fake_auth.login(instructors[0].id)
        self._verify_delete_asset(mock_asset.id, client)

    def test_student_delete_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users):
        """Student in an asset-siloed course cannot delete asset created by student in other section."""
        asset_owner, same_section_student, different_section_student = mock_asset_users
        mock_asset_course.protects_assets_per_section = True
        mock_asset.likes = 0
        mock_asset.comment_count = 0
        # Asset user in a different section cannot delete asset
        fake_auth.login(different_section_student.id)
        self._api_delete_asset(mock_asset.id, client, expected_status_code=400)
        # Asset user in asset owner's section can delete asset
        fake_auth.login(same_section_student.id)
        self._verify_delete_asset(mock_asset.id, client)

    def _verify_delete_asset(self, asset_id, client):
        self._api_delete_asset(asset_id=asset_id, client=client)
        std_commit(allow_test_environment=True)
        response = client.get(f'/api/asset/{asset_id}')
        assert response.status_code == 404


class TestLikeAsset:

    @staticmethod
    def _api_like_asset(asset_id, client, expected_status_code=200):
        response = client.post(f'/api/asset/{asset_id}/like')
        assert response.status_code == expected_status_code
        return response

    @staticmethod
    def _api_remove_like_asset(asset_id, client, expected_status_code=200):
        response = client.post(f'/api/asset/{asset_id}/remove_like')
        assert response.status_code == expected_status_code
        return response

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_like_asset(asset_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_like_asset(asset_id=1, client=client, expected_status_code=401)

    def test_like_asset_by_owner(self, client, fake_auth, mock_asset):
        """User can't like own asset."""
        fake_auth.login(mock_asset.created_by)
        self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=400)

    def test_like_asset_by_non_course_user(self, client, fake_auth, mock_asset):
        """A user in a different course can't like an asset."""
        second_course = Course.create(
            canvas_api_domain='bcourses.berkeley.edu',
            canvas_course_id=randrange(1000000),
        )
        second_course_user = User.create(
            canvas_course_role='Student',
            canvas_enrollment_state='active',
            canvas_full_name='Doug Yule',
            canvas_user_id=randrange(1000000),
            course_id=second_course.id,
        )
        fake_auth.login(second_course_user.id)
        self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=404)

    def test_like_asset_by_course_user(self, client, fake_auth, mock_asset):
        """Another user in the same court can like an asset."""
        course_users = Course.find_by_id(mock_asset.course_id).users
        different_user = next(user for user in course_users if user not in mock_asset.users)
        fake_auth.login(different_user.id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        asset_owner_points = User.find_by_id(mock_asset.created_by).points
        asset_liker_points = User.find_by_id(different_user.id).points
        assert asset['likes'] == 0
        assert asset['liked'] is False
        response = self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 1
        assert response.json['liked'] is True
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['likes'] == 1
        assert asset['liked'] is True
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 1
        assert User.find_by_id(different_user.id).points == asset_liker_points + 1
        self._api_remove_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)

    def test_student_like_asset_protected_per_section(self, client, fake_auth, mock_asset, mock_asset_course, mock_asset_users):
        """Student in an asset-siloed course cannot like asset created by student in other section."""
        asset_owner, same_section_student, different_section_student = mock_asset_users
        mock_asset_course.protects_assets_per_section = True
        # Remove the other users from the asset
        mock_asset.users = [asset_owner]
        std_commit(allow_test_environment=True)
        # Asset user in a different section cannot like asset
        fake_auth.login(different_section_student.id)
        self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=404)
        # Asset user in asset owner's section can like asset
        fake_auth.login(same_section_student.id)
        self._api_like_asset(asset_id=mock_asset.id, client=client)

    def test_likes_same_user_does_not_increment(self, client, fake_auth, mock_asset):
        course_users = Course.find_by_id(mock_asset.course_id).users
        different_user = next(user for user in course_users if user not in mock_asset.users)
        asset_owner_points = User.find_by_id(mock_asset.created_by).points
        asset_liker_points = User.find_by_id(different_user.id).points
        fake_auth.login(different_user.id)
        response = self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 1
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 1
        assert User.find_by_id(different_user.id).points == asset_liker_points + 1
        response = self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 1
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 1
        assert User.find_by_id(different_user.id).points == asset_liker_points + 1
        self._api_remove_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)

    def test_likes_multiple_users_increment_remove_likes_decrement(self, client, fake_auth, mock_asset):
        course_users = Course.find_by_id(mock_asset.course_id).users
        user_iterator = (user for user in course_users if user not in mock_asset.users and user.canvas_enrollment_state == 'active')
        different_user_1 = next(user_iterator)
        different_user_2 = next(user_iterator)
        # Clean up any point values out of sync from earlier tests.
        Activity.recalculate_points(course_id=mock_asset.course_id, user_ids=[mock_asset.created_by, different_user_1.id, different_user_2.id])
        asset_owner_points = User.find_by_id(mock_asset.created_by).points
        asset_liker_1_points = User.find_by_id(different_user_1.id).points
        asset_liker_2_points = User.find_by_id(different_user_2.id).points
        fake_auth.login(different_user_1.id)
        response = self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 1
        assert response.json['liked'] is True
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 1
        assert User.find_by_id(different_user_1.id).points == asset_liker_1_points + 1
        fake_auth.login(different_user_2.id)
        response = self._api_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 2
        assert response.json['liked'] is True
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 2
        assert User.find_by_id(different_user_2.id).points == asset_liker_2_points + 1
        fake_auth.login(different_user_1.id)
        response = self._api_remove_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 1
        assert response.json['liked'] is False
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points + 1
        assert User.find_by_id(different_user_1.id).points == asset_liker_1_points
        fake_auth.login(different_user_2.id)
        response = self._api_remove_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 0
        assert response.json['liked'] is False
        assert User.find_by_id(mock_asset.created_by).points == asset_owner_points
        assert User.find_by_id(different_user_2.id).points == asset_liker_2_points

    def test_errant_remove_like_does_not_decrement(self, client, fake_auth, mock_asset):
        course_users = Course.find_by_id(mock_asset.course_id).users
        different_user = next(user for user in course_users if user not in mock_asset.users)
        fake_auth.login(different_user.id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['likes'] == 0
        assert asset['liked'] is False
        response = self._api_remove_like_asset(asset_id=mock_asset.id, client=client, expected_status_code=200)
        assert response.json['likes'] == 0
        assert response.json['liked'] is False
