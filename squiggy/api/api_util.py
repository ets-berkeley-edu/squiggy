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

from functools import wraps

from flask import current_app as app, request
from flask_login import current_user
from squiggy.lib.util import is_admin, is_teaching, to_int
from squiggy.logger import logger
from squiggy.models.user import User


def bookmarklet_token_required(func):
    @wraps(func)
    def _bookmarklet_token_required(*args, **kw):
        user_id = request.headers.get('Squiggy-User-Id')
        bookmarklet_token = request.headers.get('Squiggy-User-Bookmarklet-Token')
        user_id = user_id and to_int(user_id)
        user = user_id and User.find_by_id(user_id)
        if user and user.bookmarklet_token == bookmarklet_token:
            return func(*args, **kw)
        else:
            logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _bookmarklet_token_required


def teacher_required(func):
    @wraps(func)
    def _teacher_required(*args, **kw):
        is_authorized = current_user.is_authenticated and (current_user.is_admin or current_user.is_teaching)
        if is_authorized:
            return func(*args, **kw)
        else:
            logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _teacher_required


def can_update_asset(user, asset):
    user_id = _get_user_id(user)
    user_ids = [user.id for user in asset.users]
    return user.course.id == asset.course_id and (is_teaching(user) or is_admin(user) or user_id in user_ids)


def can_view_asset(asset, user):
    return user and (user.course.id == asset.course_id or user.is_admin)


def can_delete_comment(comment, user):
    user_id = _get_user_id(user)
    return user_id and (comment.user_id == user_id or user.is_admin or user.is_teaching)


def can_update_comment(comment, user):
    user_id = _get_user_id(user)
    return user_id and (comment.user_id == user_id or user.is_admin or user.is_teaching)


def _get_user_id(user):
    return user and (user.id if hasattr(user, 'id') else user.user_id)
