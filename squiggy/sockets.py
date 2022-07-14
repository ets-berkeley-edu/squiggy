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

from flask import request
from flask_login import current_user, login_required
from flask_socketio import emit, join_room, leave_room
from squiggy.api.api_util import get_socket_io_room
from squiggy.lib.util import is_student, isoformat, utc_now
from squiggy.logger import initialize_background_logger
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_session import WhiteboardSession


def register_sockets(socketio):
    logger = initialize_background_logger(
        name='whiteboard_sockets',
        location='whiteboard_sockets.log',
    )

    @socketio.on('join')
    @login_required
    def socketio_join(data):
        socket_id = request.sid
        whiteboard_id = data.get('whiteboardId')
        logger.debug(f'socketio_join: {data}')
        if is_student(current_user):
            WhiteboardSession.update_updated_at(
                socket_id=socket_id,
                user_id=current_user.user_id,
                whiteboard_id=whiteboard_id,
            )
            room = get_socket_io_room(whiteboard_id)
            join_room(room, sid=socket_id)
            emit(
                'join',
                current_user.user_id,
                broadcast=True,
                include_self=False,
                skip_sid=socket_id,
                to=room,
            )
        return {'status': 200}

    @socketio.on('leave')
    @login_required
    def socketio_leave(data):
        whiteboard_id = data.get('whiteboardId')
        logger.debug(f'socketio_leave: user_id = {current_user}, whiteboard_id = {whiteboard_id}')
        if is_student(current_user):
            socket_id = request.sid
            WhiteboardSession.delete_all([socket_id], older_than_minutes=1440)
            room = get_socket_io_room(whiteboard_id)
            leave_room(room, sid=socket_id)
            emit(
                'leave',
                current_user.user_id,
                include_self=False,
                skip_sid=socket_id,
                to=room,
            )
        return {'status': 200}

    @socketio.on('update_whiteboard')
    @login_required
    def socketio_update_whiteboard(data):
        socket_id = request.sid
        title = data.get('title')
        users = User.find_by_ids(data.get('userIds'))
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        logger.debug(f'socketio_update_whiteboard: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        Whiteboard.update(title=title, users=users, whiteboard_id=whiteboard_id)
        emit(
            'update_whiteboard',
            {
                'title': title,
                'users': [user.to_api_json() for user in users],
                'whiteboardId': whiteboard_id,
            },
            include_self=False,
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
        if is_student(current_user):
            WhiteboardSession.update_updated_at(
                socket_id=socket_id,
                user_id=current_user.user_id,
                whiteboard_id=whiteboard_id,
            )
        return {'status': 200}

    @socketio.on('boo-boo-kitty')
    def socketio_boo_boo_kitty(data):
        logger.debug(f'socketio_boo_boo_kitty: {data}')
        emit(
            'boo-boo-kitty',
            {
                'message': isoformat(utc_now()),
            },
            broadcast=True,
            include_self=True,
        )
        return {'status': 200}

    @socketio.on('connect')
    @login_required
    def socketio_connect():
        logger.debug('socketio_connect')

    @socketio.on('disconnect')
    def socketio_disconnect():
        logger.debug('socketio_disconnect')

    @socketio.on_error()
    def socketio_error(e):
        logger.error(f'socketio_error: {e}')

    @socketio.on_error_default
    def socketio_error_default(e):
        logger.error(f'socketio_error_default: {e}')
