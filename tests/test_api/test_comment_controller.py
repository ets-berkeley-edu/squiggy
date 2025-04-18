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

from tests.test_api.test_asset_controller import _api_get_asset

unauthorized_user_id = '666'


class TestGetComments:

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


def _api_get_comments(asset_id, client, expected_status_code=200):
    response = client.get(f'/api/comments/{asset_id}')
    assert response.status_code == expected_status_code
    return response.json
