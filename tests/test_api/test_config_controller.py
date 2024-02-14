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

from squiggy.models.asset import assets_type


class TestConfigController:

    def test_anonymous(self, client):
        """Do not deny the anonymous user."""
        assert client.get('/api/config').status_code == 200

    def test_feature_flag(self, client):
        """Asset types include 'whiteboard'."""
        response = client.get('/api/config')
        assert response.status_code == 200
        assert response.json['assetTypes'] == assets_type.enums

    def test_logged_in(self, client, fake_auth, authorized_user_id):
        """Returns a well-formed response to logged-in user."""
        fake_auth.login(authorized_user_id)
        response = client.get('/api/config')
        assert response.status_code == 200
        assert 'squiggyEnv' in response.json
        data = response.json
        assert data['assetTypes'] == ['file', 'link', 'whiteboard']
        assert data['ebEnvironment'] is None
        assert data['timezone'] == 'America/Los_Angeles'

    def test_anonymous_version_request(self, client):
        """Returns a well-formed response."""
        response = client.get('/api/version')
        assert response.status_code == 200
        assert 'version' in response.json
        assert 'build' in response.json
