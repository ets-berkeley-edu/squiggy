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

import csv
import tempfile

from flask import current_app as app
from squiggy.api.api_util import admin_required
from squiggy.lib.errors import ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.prod_data_importer import get_prod_data_importer_sql, safe_execute_prod_data_importer_sql


@app.route('/api/schlemiel/schlimazel/hasenpfeffer_incorporated')
@admin_required
def import_prod_data():
    if _is_prod_data_importer_enabled():
        canvas_api_domain = app.config['PROD_DATA_IMPORTER_CANVAS_API_DOMAIN']
        # TODO: Include all squiggy db tables.
        db_tables = ['activities']
        with tempfile.TemporaryDirectory() as temp_directory:
            for db_table in db_tables:
                sql = get_prod_data_importer_sql(table_name=db_table, canvas_api_domain=canvas_api_domain)
                rows = safe_execute_prod_data_importer_sql(sql)
                _write_csv(f'{temp_directory}/{db_table}.csv', rows)
                # TODO: load CSV data to local db.
            return tolerant_jsonify({})
    else:
        raise ResourceNotFoundError('Vo-dee-oh-doh-doh!')


def _is_prod_data_importer_enabled():
    is_production = 'prod' in app.config.get('EB_ENVIRONMENT', '').lower()
    return not is_production and app.config['FEATURE_FLAG_PROD_DATA_IMPORTER']


def _write_csv(filename, rows):
    with open(filename, 'w') as csvfile:
        if rows:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
