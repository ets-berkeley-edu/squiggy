"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
https://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

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
from sqlalchemy.exc import SQLAlchemyError
from squiggy import db
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import utc_now
from squiggy.logger import logger


@app.route('/api/ping')
def app_status():
    resp = {
        'app': True,
        'db': _db_status(),
        'poller': _poller_status(),
        'whiteboards': _whiteboard_housekeeping_status(),
    }
    return tolerant_jsonify(resp)


def _db_status():
    try:
        db.session.execute('SELECT 1')
        return True
    except SQLAlchemyError:
        logger.exception('Database connection error')
        return False


def _poller_status():
    try:
        first_row = db.session.execute('SELECT last_polled FROM courses WHERE last_polled IS NOT NULL ORDER BY last_polled DESC LIMIT 1').first()
        if first_row:
            diff_in_hours = (utc_now() - first_row['last_polled']).total_seconds() / 3600
            return diff_in_hours < app.config['CANVAS_POLLER_ACCEPTABLE_HOURS_SINCE_LAST']
        else:
            return False
    except SQLAlchemyError:
        logger.exception('Database connection error')
        return None


def _whiteboard_housekeeping_status():
    try:
        first_row = db.session.execute("SELECT last_run FROM background_jobs WHERE job_name = 'whiteboard_housekeeping'").first()
        if first_row:
            diff_in_minutes = (utc_now() - first_row['last_run']).total_seconds() / 60
            return diff_in_minutes < app.config['WHITEBOARD_HOUSEKEEPING_ACCEPTABLE_MINUTES_SINCE_LAST']
        else:
            return False
    except SQLAlchemyError:
        logger.exception('Database connection error')
        return None
