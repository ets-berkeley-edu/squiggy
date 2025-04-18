"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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
from datetime import datetime

from flask import current_app as app
import pytz
from sqlalchemy.exc import SQLAlchemyError
from squiggy import db
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.previews import ping_preview_service
from squiggy.lib.util import utc_now
from squiggy.logger import logger


@app.route('/api/ping')
def app_status():
    resp = {
        'app': True,
        'cache': _cache_status(),
        'db': _db_status(),
        'poller': _poller_status(),
        'previewService': _preview_service_status(),
        'whiteboards': _whiteboard_housekeeping_status(),
    }
    return tolerant_jsonify(resp)


@app.route('/api/countdown')
def countdown():

    def _calculate_countdown(countdown):
        td = datetime.fromisoformat(countdown).astimezone(pytz.timezone(app.config['TIMEZONE'])) - utc_now()
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'days': td.days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
        }

    resp = {
        'readonly': _calculate_countdown(app.config['COUNTDOWN_READONLY']),
        'removal': _calculate_countdown(app.config['COUNTDOWN_REMOVAL']),
    }
    return tolerant_jsonify(resp)


def _cache_status():
    # Sockets and background jobs have been turned off; don't bother Nagios.
    return True


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


def _preview_service_status():
    return ping_preview_service()


def _whiteboard_housekeeping_status():
    # Whiteboard housekeeping has been turned off; don't bother Nagios.
    return True
