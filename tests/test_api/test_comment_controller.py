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
        api_json = self._api_create_comment(
            asset_id=mock_asset.id,
            body='I\'m in the phone booth, it\'s the one across the hall',
            client=client,
        )
        comment_id = api_json['id']
        assert comment_id
        assert 'phone booth' in api_json['body']
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


def _api_get_comments(asset_id, client, expected_status_code=200):
    response = client.get(f'/api/comments/{asset_id}')
    assert response.status_code == expected_status_code
    return response.json
