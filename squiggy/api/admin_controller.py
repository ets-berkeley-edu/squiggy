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

import tempfile

from flask import current_app as app
from squiggy.api.api_util import admin_required
from squiggy.lib.errors import ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.prod_data_importer import write_prod_data_csv_files


@app.route('/api/schlemiel/schlimazel/hasenpfeffer_incorporated')
@admin_required
def import_prod_data():
    if _is_prod_data_importer_enabled():
        with tempfile.TemporaryDirectory() as temp_directory:
            write_prod_data_csv_files(temp_directory)
            return tolerant_jsonify({})
    else:
        raise ResourceNotFoundError('Vo-dee-oh-doh-doh!')


def _is_prod_data_importer_enabled():
    is_production = 'prod' in app.config.get('EB_ENVIRONMENT', '').lower()
    return not is_production and app.config['FEATURE_FLAG_PROD_DATA_IMPORTER']
