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

from moto import mock_s3
from squiggy.lib.util import is_teaching
from squiggy.models.asset import Asset
from squiggy.models.course import Course
from squiggy.models.user import User

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

    def test_view_protected_asset(self, client, fake_auth, mock_asset, mock_asset_course):
        """Student in an asset-siloed course cannot view asset created by student in other section."""
        course = mock_asset_course
        course.protects_assets_per_section = True

        section_a_student = User.query.filter_by(course_id=course.id, canvas_course_role='Student',
                                                 canvas_course_sections=['section A']).first()
        fake_auth.login(section_a_student.id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['id'] == mock_asset.id

        section_b_student = User.query.filter_by(course_id=course.id, canvas_course_role='Student',
                                                 canvas_course_sections=['section B']).first()
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
            group_id=None,
            keywords=None,
            limit=20,
            offset=0,
            order_by=None,
            section=None,
            user_id=None,
    ):
        params = {
            'assetType': asset_type,
            'categoryId': category_id,
            'groupId': group_id,
            'keywords': keywords,
            'limit': limit,
            'offset': offset,
            'orderBy': order_by,
            'section': section,
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
            for key in (
                'id',
                'canvasFullName',
                'canvasUserId',
                'canvasCourseRole',
                'canvasEnrollmentState',
                'canvasCourseSections',
                'canvasImage',
            ):
                assert key in asset['users'][0]

    def test_teacher_assets_protected_per_section(self, authorized_user_id, client, fake_auth, mock_asset_course):
        """Teacher in an asset-siloed course can see all assets for the course."""
        mock_asset_course.protects_assets_per_section = True
        # Instructor can see all assets for the course
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        api_json = self._api_get_assets(client)
        assert api_json['total'] > 2
        assert next(
            asset for asset in api_json['results'] if asset['users'][0]['canvasCourseSections'] == ['section A'])
        assert next(
            asset for asset in api_json['results'] if asset['users'][0]['canvasCourseSections'] == ['section B'])
        assert next(asset for asset in api_json['results'] if asset['users'][0]['canvasCourseRole'] != 'Student')

    def test_teacher_assets_protected_per_section_with_filter(
            self,
            authorized_user_id,
            client,
            fake_auth,
            mock_asset_course,
    ):
        """Teacher in an asset-siloed course sees assets for a specific section when filter is applied."""
        mock_asset_course.protects_assets_per_section = True
        user = User.find_by_id(authorized_user_id)
        fake_auth.login(user.id)
        for section in ('section A', 'section B'):
            # Filter results for a specific section
            api_json = self._api_get_assets(client, section=section)
            assert len(api_json['results'])
            for asset in api_json['results']:
                for user in asset['users']:
                    for canvas_section in user['canvasCourseSections']:
                        assert canvas_section == section

    def test_student_assets_protected_per_section(self, client, fake_auth, mock_asset_course):
        """Student in an asset-siloed course can see assets created by teacher or other student in their section."""
        mock_asset_course.protects_assets_per_section = True
        # Students can see the instructor's assets plus any other assets for their section
        for section in ('section A', 'section B'):
            student = User.query.filter_by(
                course_id=mock_asset_course.id,
                canvas_course_role='Student',
                canvas_course_sections=[section],
            ).first()
            fake_auth.login(student.id)
            api_json = self._api_get_assets(client)
            assert api_json['total'] > 1
            for asset in api_json['results']:
                assert len(asset['users']) == 1
                assert asset['users'][0]['canvasCourseRole'] != 'Student' or asset['users'][0][
                    'canvasCourseSections'] == [section]

    def test_get_assets_per_group(self, client, fake_auth, mock_course_group):
        """Search returns assets from the specified group."""
        membership1 = mock_course_group.memberships[0]
        membership2 = mock_course_group.memberships[1]
        student1 = User.find_by_course_id(membership1.canvas_user_id, membership1.course_id)
        student2 = User.find_by_course_id(membership2.canvas_user_id, membership2.course_id)
        fake_auth.login(student2.id)
        asset1 = Asset.create(
            asset_type='link',
            course_id=mock_course_group.course_id,
            created_by=student1.id,
            title='mock link',
            users=[],
            url='https://www.example.com',
        )
        api_json = self._api_get_assets(
            client=client,
            asset_type='link',
            group_id=mock_course_group.id,
        )
        assert api_json['total'] == 1
        assert api_json['results'][0]['id'] == asset1.id
        bogus_group_id = mock_course_group.id + 1
        api_json = self._api_get_assets(
            client=client,
            asset_type='link',
            group_id=bogus_group_id,
        )
        assert api_json['total'] == 0
