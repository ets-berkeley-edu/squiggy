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

import pytest
from squiggy.models.activity import Activity
from squiggy.models.asset import Asset


unauthorized_user_id = 666


@pytest.mark.usefixtures('db_session')
class TestAsset:

    def test_assets_for_course(self, authorized_user_session):
        asset_feed = Asset.get_assets(authorized_user_session, order_by='recent', offset=0, limit=20, filters={})
        # Feed shape
        assert asset_feed['offset'] == 0
        assert asset_feed['total'] == len(asset_feed['results'])
        # Ordering
        assert asset_feed['results'][0]['id'] > asset_feed['results'][1]['id']
        # Asset structure
        for asset in asset_feed['results']:
            assert asset['body'] is None
            assert asset['canvasAssignmentId'] is None
            assert asset['commentCount'] == 0
            assert asset['courseId'] == authorized_user_session.course.id
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
            assert asset['users'][0]['id'] == authorized_user_session.user.id
            assert asset['users'][0]['canvasFullName'] == 'Oliver Heyer'
            assert asset['users'][0]['canvasUserId'] == 9876543
            assert asset['users'][0]['canvasCourseRole'] == 'Teacher'
            assert asset['users'][0]['canvasEnrollmentState'] == 'active'
            assert 'canvasCourseSections' in asset['users'][0]
            assert 'canvasImage' in asset['users'][0]

    def test_asset_creation_activity(self, authorized_user_session):
        asset = Asset.create(
            asset_type='link',
            categories=None,
            course_id=authorized_user_session.course.id,
            title='Riding in a Stutz Bear Cat, Jim',
            url='https://genius.com/The-velvet-underground-sweet-jane-lyrics',
            users=[authorized_user_session.user],
        )
        activities = Activity.query.filter_by(asset_id=asset.id).all()
        assert len(activities) == 1
        assert activities[0].activity_type == 'asset_add'
        assert activities[0].course_id == authorized_user_session.course.id
        assert activities[0].object_type == 'asset'
        assert activities[0].object_id == asset.id
        assert activities[0].asset_id == asset.id
        assert activities[0].user_id == authorized_user_session.user.id

    def test_asset_creation_invisible_no_activities(self, authorized_user_session):
        asset = Asset.create(
            asset_type='link',
            categories=None,
            course_id=authorized_user_session.course.id,
            title='Riding in a Stutz Bear Cat, Jim',
            url='https://genius.com/The-velvet-underground-sweet-jane-lyrics',
            users=[authorized_user_session.user],
            visible=False,
        )
        activities = Activity.query.filter_by(asset_id=asset.id).all()
        assert len(activities) == 0
