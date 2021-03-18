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

from datetime import datetime

from squiggy.lib.previews import generate_preview_service_signature


class TestPreviews:
    """Preview service callback API."""

    @classmethod
    def _api_post_preview_callback(cls, client, auth_header, params, expected_status_code=200):
        response = client.post(
            '/api/previews/callback',
            headers={'authorization': auth_header},
            data=params,
            content_type='multipart/form-data',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_missing_header(self, client):
        """Deny missing header."""
        self._api_post_preview_callback(client, None, {}, expected_status_code=401)

    def test_malformed_header(self, client):
        """Deny malformed header."""
        self._api_post_preview_callback(client, 'back off boogaloo', {}, expected_status_code=401)

    def test_expired_header(self, client):
        """Deny expired header."""
        header = generate_preview_service_signature(str((int(datetime.now().timestamp() - 800) * 1000000)))
        self._api_post_preview_callback(client, header, {}, expected_status_code=401)

    def test_valid_header_missing_parameters(self, client):
        """Require id and status parameters."""
        header = generate_preview_service_signature()
        self._api_post_preview_callback(client, header, {}, expected_status_code=400)

    def test_invalid_asset_id(self, client):
        """Require valid asset id."""
        header = generate_preview_service_signature()
        self._api_post_preview_callback(client, header, {'id': 87654, 'status': 'done'}, expected_status_code=400)

    def test_valid_asset_id(self, client, db_session, mock_asset):
        """Updates when provided with valid asset id."""
        assert mock_asset.image_url is None
        assert mock_asset.thumbnail_url is None
        assert mock_asset.preview_status == 'pending'
        assert mock_asset.preview_metadata == '{}'

        header = generate_preview_service_signature()
        preview_result_payload = {
            'id': mock_asset.id,
            'status': 'done',
            'image': 'https://imgur.com/gallery/6LXFXr2',
            'thumbnail': 'https://imgur.com/gallery/QZmb5KU',
            'metadata': '{"imageWidth": 200, "imageHeight": 100}',
        }
        self._api_post_preview_callback(client, header, preview_result_payload)

        assert mock_asset.preview_status == 'done'
        assert mock_asset.image_url == 'https://imgur.com/gallery/6LXFXr2'
        assert mock_asset.thumbnail_url == 'https://imgur.com/gallery/QZmb5KU'
        assert mock_asset.preview_metadata == {'imageWidth': 200, 'imageHeight': 100}
