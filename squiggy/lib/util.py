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

from datetime import datetime

from dateutil.tz import tzutc
from flask import current_app as app
import pytz


def camelize(string):
    def lower_then_capitalize():
        yield str.lower
        while True:
            yield str.capitalize
    string_transform = lower_then_capitalize()
    return ''.join(next(string_transform)(segment) for segment in string.split('_'))


def db_row_to_dict(row):
    d = dict(row)
    json_obj = dict()
    for key in d.keys():
        value = d[key]
        if key.endswith('_at') or isinstance(value, datetime):
            json_obj[camelize(key)] = isoformat(value)
        elif isinstance(value, dict):
            json_obj[camelize(key)] = db_row_to_dict(value)
        else:
            json_obj[camelize(key)] = value
    return json_obj


def get_user_id(user):
    return user and (user.id if hasattr(user, 'id') else user.user_id)


def is_admin(user):
    canvas_course_role = _get_canvas_course_role(user)
    return 'admin' in (canvas_course_role or '').lower()


def is_student(user):
    canvas_course_role = (_get_canvas_course_role(user) or '').lower()
    return 'student' in canvas_course_role or 'learner' in canvas_course_role


def is_observer(user):
    canvas_course_role = _get_canvas_course_role(user)
    return 'observer' in (canvas_course_role or '').lower()


def is_teaching(user):
    canvas_course_role = (_get_canvas_course_role(user) or '').lower()
    return 'instructor' in canvas_course_role or 'teacher' in canvas_course_role


def isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()


def local_now():
    return utc_now().astimezone(pytz.timezone(app.config['TIMEZONE']))


def safe_strip(s):
    return str(s).strip() if isinstance(s, str) else None


def to_bool_or_none(arg):
    """
    With the idea of "no decision is a decision" in mind, this util has three possible outcomes: True, False and None.

    If arg is type string then intuitively handle 'true'/'false' values, else return None.
    If arg is NOT type string and NOT None then rely on Python's bool().
    """
    s = arg
    if isinstance(arg, str):
        s = arg.strip().lower()
        s = True if s == 'true' else s
        s = False if s == 'false' else s
        s = None if s not in [True, False] else s
    return None if s is None else bool(s)


def to_int(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def _get_canvas_course_role(user):
    if type(user) is dict:
        return user.get('canvasCourseRole') or user.get('canvas_course_role')
    else:
        return user.canvas_course_role
