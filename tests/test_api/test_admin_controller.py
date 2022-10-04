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
from squiggy.lib.util import is_admin
from squiggy.models.user import User
from tests.util import override_config


class TestProdDataImporter:
    """API to import production data to local Squiggy db (test environment)."""

    @classmethod
    def _api_import_prod_data(cls, client, expected_status_code=200):
        response = client.get('/api/schlemiel/schlimazel/hasenpfeffer_incorporated')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, app, client):
        """Denies anonymous user."""
        with override_config(app, 'FEATURE_FLAG_PROD_DATA_IMPORTER', True):
            self._api_import_prod_data(client, expected_status_code=401)

    def test_unauthorized(self, app, client, fake_auth):
        """Denies teacher."""
        with override_config(app, 'FEATURE_FLAG_PROD_DATA_IMPORTER', True):
            instructor = User.query.filter_by(canvas_course_role='Teacher').first()
            fake_auth.login(instructor.id)
            self._api_import_prod_data(client, expected_status_code=401)

    def test_authorized(self, app, client, fake_auth):
        """Admin user can run prod-data-import job."""
        admin = User.query.filter_by(canvas_course_role='Administrator').first()
        assert is_admin(admin)
        fake_auth.login(admin.id)
        with override_config(app, 'FEATURE_FLAG_PROD_DATA_IMPORTER', False):
            self._api_import_prod_data(client, 404)

        with override_config(app, 'FEATURE_FLAG_PROD_DATA_IMPORTER', True):
            self._api_import_prod_data(client)
