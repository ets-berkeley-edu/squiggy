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
from flask import current_app as app
from tests.util import override_config


class TestCanvasDomains:
    """Canvas API."""

    @classmethod
    def _api_get_canvas_domains(cls, client, expected_status_code=200):
        response = client.get('/api/canvas/all_domains')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Deny anonymous user."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', False):
            self._api_get_canvas_domains(client, expected_status_code=401)

    def test_anonymous_when_dev_auth(self, client):
        """Allow when DEVELOPER_AUTH_ENABLED."""
        with override_config(app, 'DEVELOPER_AUTH_ENABLED', True):
            api_json = self._api_get_canvas_domains(client)
            assert len(api_json)
            assert 'canvasApiDomain' in api_json[0]
