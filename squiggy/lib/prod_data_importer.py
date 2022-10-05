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

from contextlib import contextmanager
import csv
from datetime import datetime

from flask import current_app as app
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from squiggy.lib.prod_data_importer_sql_factory import get_prod_data_importer_sql
from squiggy.logger import logger

connection_pool = None

# In the following list, order matters.
DB_TABLES_TO_IMPORT_FROM_PROD = [
    # Db tables that contain no references to specific Canvas hostnames.
    'activities',
    'activity_types',
    'asset_categories',
    'asset_users',
    'categories',
    'comments',
    'whiteboard_members',
    'users',
    # Next, tables that contain references to specific Canvas hostnames.
    'assets',
    'asset_whiteboard_elements',
    'courses',
    'whiteboards',
    'whiteboard_elements',
]


def write_prod_data_csv_files(directory):
    for db_table in DB_TABLES_TO_IMPORT_FROM_PROD:
        try:
            sql = get_prod_data_importer_sql(db_table)
            rows = _safe_execute_prod_data_importer_sql(sql)
            _write_csv(f'{directory}/{db_table}.csv', rows)
            # TODO: load CSV data to local db.
        except Exception as e:
            logger.error(f'Prod data import failed on database table \'{db_table}\'')
            raise e


@contextmanager
def _cursor_from_pool():
    try:
        connection = connection_pool.getconn()
        yield connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    finally:
        connection_pool.putconn(connection)


def _safe_execute(sql, cursor, **kwargs):
    try:
        ts = datetime.now().timestamp()
        cursor.execute(sql, kwargs)
        query_time = datetime.now().timestamp() - ts
    except psycopg2.Error as e:
        app.logger.error(f'SQL {sql} threw {e}')
        return None
    rows = [dict(r) for r in cursor.fetchall()]
    app.logger.debug(f'Query returned {len(rows)} rows in {query_time} seconds:\n{sql}\n{kwargs}')
    return rows


def _safe_execute_prod_data_importer_sql(string, **kwargs):
    if app.config['TESTING']:
        return []
    else:
        global connection_pool
        if connection_pool is None:
            connection_pool = ThreadedConnectionPool(1, 1, app.config['PROD_DATA_IMPORTER_SOURCE_URI'])
        with _cursor_from_pool() as cursor:
            return _safe_execute(string, cursor, **kwargs)


def _write_csv(filename, rows):
    with open(filename, 'w') as csvfile:
        if rows:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
