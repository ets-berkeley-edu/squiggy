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

from squiggy import std_commit
from squiggy.lib.util import is_admin, is_teaching
from squiggy.models.activity import Activity
from squiggy.models.comment import Comment
from squiggy.models.course import Course
from squiggy.models.user import User
from tests.test_api.test_asset_controller import _api_get_asset

unauthorized_user_id = '666'


class TestCreateComments:
    """Create Comment API."""

    @classmethod
    def _api_create_comment(cls, asset_id, body, client, parent_id=None, expected_status_code=200):
        params = {
            'assetId': asset_id,
            'body': body,
            'parentId': parent_id,
        }
        response = client.post(
            '/api/comment/create',
            data=json.dumps(params),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_comment(asset_id=1, body='Body', client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_create_comment(asset_id=1, body='Body', client=client, expected_status_code=401)

    def test_admin(self, authorized_user_id, client, fake_auth, mock_asset):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        initial_comment_count = asset['commentCount']
        assert initial_comment_count > 0
        api_json = self._api_create_comment(
            asset_id=mock_asset.id,
            body='I\'m in the phone booth, it\'s the one across the hall',
            client=client,
        )
        comment_id = api_json['id']
        assert comment_id
        assert 'phone booth' in api_json['body']
        # Verify activities
        activities = Activity.find_by_object_id(object_type='comment', object_id=comment_id)
        assert len(activities) > 0
        assert activities[0].asset_id == mock_asset.id
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['commentCount'] == initial_comment_count + 1

        # Reply
        self._api_create_comment(
            asset_id=mock_asset.id,
            body='If you don\'t answer, I\'ll just ring it off the wall',
            client=client,
            parent_id=comment_id,
        )
        # Verify
        api_json = _api_get_comments(asset_id=mock_asset.id, client=client)
        comment = api_json[0]
        assert 'phone booth' in comment['body']
        assert 'replies' in comment
        replies = comment['replies']
        assert len(replies) == 1
        assert 'ring it off the wall' in replies[0]['body']
        activities = Activity.find_by_object_id(object_type='comment', object_id=replies[0]['id'])
        assert len(activities) > 0
        assert activities[0].asset_id == mock_asset.id
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['commentCount'] == initial_comment_count + 2


class TestGetComments:
    """Comment API."""

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_comments(asset_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_get_comments(asset_id=1, client=client, expected_status_code=401)

    def test_admin(self, authorized_user_id, client, fake_auth, mock_asset):
        """Returns a well-formed response."""
        fake_auth.login(authorized_user_id)
        api_json = _api_get_comments(asset_id=mock_asset.id, client=client)
        assert len(api_json) == 2
        comment = api_json[1]
        assert comment.get('user', {}).get('id') == comment['userId']
        assert 'replies' in comment
        replies = comment['replies']
        assert len(replies) == 2
        assert 'all tomorrow\'s parties' in replies[0]['body']
        assert 'Sunday\'s clown' in replies[1]['body']
        asset = _api_get_asset(asset_id=mock_asset.id, client=client)
        assert asset['commentCount'] == 4


class TestUpdateComment:
    """Update comment API."""

    @staticmethod
    def _api_update_comment(client, body, comment_id, expected_status_code=200):
        response = client.post(
            f'/api/comment/{comment_id}/update',
            data=json.dumps({'body': body}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return json.loads(response.data)

    def test_anonymous(self, client, mock_asset):
        """Denies anonymous user."""
        self._api_update_comment(client, body='Anonymous hack!', comment_id=1, expected_status_code=401)

    def test_teachers_cannot_update(self, client, fake_auth):
        """Denies teacher."""
        instructor = next(user for user in User.query.all() if is_teaching(user))
        fake_auth.login(instructor.id)
        self._api_update_comment(
            client,
            body='Unauthorized instructor hack!',
            comment_id=1,
            expected_status_code=404,
        )

    def test_admins_cannot_update(self, client, fake_auth):
        """Denies admin."""
        admin_user = next(user for user in User.query.all() if is_admin(user))
        fake_auth.login(admin_user.id)
        self._api_update_comment(
            client,
            body='Unauthorized admin hack!',
            comment_id=1,
            expected_status_code=404,
        )

    def test_update_comment_by_owner(self, client, fake_auth, mock_asset):
        """Comment author can update comment."""
        comment = Comment.query.first()
        fake_auth.login(comment.user_id)
        body = 'I, me, mine.'
        self._api_update_comment(client, body=body, comment_id=comment.id)
        std_commit(allow_test_environment=True)
        # Verify update
        comments = _api_get_comments(asset_id=comment.asset_id, client=client)
        updated_comment = next(c for c in comments if c['id'] == comment.id)
        assert updated_comment['body'] == body


class TestDeleteComment:
    """Delete comment API."""

    @staticmethod
    def _api_delete_comment(comment_id, client, expected_status_code=200):
        response = client.delete(f'/api/comment/{comment_id}/delete')
        assert response.status_code == expected_status_code

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_delete_comment(comment_id=1, client=client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        self._api_delete_comment(comment_id=1, client=client, expected_status_code=401)

    def test_delete_comment_by_owner(self, client, fake_auth, mock_asset):
        """Authorized user can delete comment."""
        fake_auth.login(mock_asset.users[0].id)
        self._verify_delete_comment(mock_asset, client)

    def test_delete_asset_by_teacher(self, client, fake_auth, mock_asset):
        """Authorized user can delete asset."""
        course = Course.find_by_id(mock_asset.course_id)
        instructors = list(filter(lambda u: is_teaching(u), course.users))
        fake_auth.login(instructors[0].id)
        self._verify_delete_comment(mock_asset, client)

    def _verify_delete_comment(self, asset, client):
        asset_feed = _api_get_asset(asset_id=asset.id, client=client)
        initial_comment_count = asset_feed['commentCount']
        assert initial_comment_count > 0
        comment = Comment.get_comments(asset_id=asset.id)[0]
        comment_id = comment['id']
        self._api_delete_comment(comment_id=comment_id, client=client)
        std_commit(allow_test_environment=True)
        comments = _api_get_comments(asset_id=asset.id, client=client)
        comment_ids = list(map(lambda c: c['id'], comments))
        assert comment_id not in comment_ids
        asset_feed = _api_get_asset(asset_id=asset.id, client=client)
        assert asset_feed['commentCount'] == initial_comment_count - 1
        activities = Activity.find_by_object_id(object_type='comment', object_id=comment_id)
        assert len(activities) == 0


def _api_get_comments(asset_id, client, expected_status_code=200):
    response = client.get(f'/api/comments/{asset_id}')
    assert response.status_code == expected_status_code
    return response.json
