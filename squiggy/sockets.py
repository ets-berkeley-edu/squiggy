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
from flask_socketio import emit, join_room, leave_room
from squiggy.api.whiteboard_socket_handler import check_for_updates, delete_whiteboard_element, join_whiteboard, \
    leave_whiteboard, update_whiteboard, upsert_whiteboard_element
from squiggy.lib.login_session import LoginSession
from squiggy.logger import initialize_background_logger
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard


def register_sockets(socketio):
    logger = initialize_background_logger(
        name='whiteboard_sockets',
        location='whiteboard_sockets.log',
    )

    def _get_room(whiteboard_id):
        return f'whiteboard-{whiteboard_id}'

    @socketio.on('kitty')
    def socketio_kitty(data):
        socket_id = request.sid
        whiteboard_id = data.get('whiteboardId')
        room = _get_room(whiteboard_id)
        leave_room(room, sid=socket_id)
        whiteboard = Whiteboard.find_by_id(current_user=None, whiteboard_id=whiteboard_id)
        logger.debug(f'socketio_kitty: whiteboard_id = {whiteboard_id}')
        emit(
            'kitty',
            whiteboard,
            to=room,
        )

    @socketio.on('join')
    def socketio_join(data):
        socket_id = request.sid
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        whiteboard = join_whiteboard(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
        )
        room = _get_room(whiteboard_id)
        join_room(room, sid=socket_id)
        logger.debug(f'socketio_join: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        emit(
            'join',
            whiteboard,
            broadcast=True,
            include_self=False,
            skip_sid=socket_id,
            to=room,
        )
        whiteboard = Whiteboard.find_by_id(
            current_user=LoginSession(user_id),
            whiteboard_id=whiteboard_id,
        )
        return whiteboard['users']

    @socketio.on('leave')
    def socketio_leave(data):
        socket_id = request.sid
        user_id = data.get('userId')
        current_user = LoginSession(user_id)
        whiteboard_id = data.get('whiteboardId')
        leave_whiteboard(
            current_user=current_user,
            socket_id=request.sid,
            whiteboard_id=whiteboard_id,
        )
        room = _get_room(whiteboard_id)
        leave_room(room, sid=socket_id)
        whiteboard = Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
        logger.debug(f'socketio_leave: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        emit(
            'leave',
            whiteboard,
            include_self=False,
            skip_sid=socket_id,
            to=room,
        )

    @socketio.on('update_whiteboard')
    def socketio_update_whiteboard(data):
        socket_id = request.sid
        title = data.get('title')
        users = User.find_by_ids(data.get('userIds'))
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        logger.debug(f'socketio_update_whiteboard: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        update_whiteboard(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            title=title,
            users=users,
        )
        emit(
            'update_whiteboard',
            {
                'title': title,
                'users': [user.to_api_json() for user in users],
                'whiteboardId': whiteboard_id,
            },
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('upsert_whiteboard_element')
    def socketio_upsert_whiteboard_element(data):
        socket_id = request.sid
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        whiteboard_element = upsert_whiteboard_element(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            whiteboard_element=data.get('whiteboardElement'),
        )
        logger.debug(f'socketio_upsert_whiteboard_element: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        emit(
            'upsert_whiteboard_element',
            {
                'whiteboardElement': whiteboard_element,
                'whiteboardId': whiteboard_id,
            },
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('delete_whiteboard_element')
    def socketio_delete(data):
        socket_id = request.sid
        user_id = data.get('userId')
        whiteboard_element = data.get('whiteboardElement')
        whiteboard_id = data.get('whiteboardId')
        delete_whiteboard_element(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            whiteboard_element=whiteboard_element,
        )
        logger.debug(f'socketio_delete: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        emit(
            'delete_whiteboard_element',
            {
                'uuid': whiteboard_element['element']['uuid'],
                'whiteboardId': whiteboard_id,
            },
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('check_for_updates')
    def socketio_check_for_updates(data):
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        logger.debug(f'socketio_check_for_updates: user_id = {user_id}, whiteboard_id = {whiteboard_id}')
        return check_for_updates(
            current_user=LoginSession(user_id),
            socket_id=request.sid,
            whiteboard_id=whiteboard_id,
        )

    @socketio.on('disconnect')
    def socketio_disconnect():
        logger.debug('socketio_disconnect')
        pass
