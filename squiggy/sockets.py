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

from flask_socketio import emit
from squiggy.api.api_whiteboard_util import create_whiteboard_elements, delete_whiteboard_elements, \
    join_whiteboard, leave_whiteboard, update_updated_at, update_whiteboard, update_whiteboard_elements
from squiggy.lib.login_session import LoginSession
from squiggy.models.user import User


def register_sockets(socketio):

    @socketio.on('join')
    def socketio_join(data):
        socket_id = data.get('socketId')
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        join_whiteboard(
            socket_id=data.get('socketId'),
            user=LoginSession(user_id),
            whiteboard_id=whiteboard_id,
        )
        emit(
            'join',
            {
                'socketId': socket_id,
                'userId': user_id,
                'whiteboardId': whiteboard_id,
            },
        )

    @socketio.on('leave')
    def socketio_leave(data):
        socket_id = data.get('socketId')
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        leave_whiteboard(
            socket_id=data.get('socketId'),
            user=LoginSession(user_id),
            whiteboard_id=whiteboard_id,
        )
        emit(
            'leave',
            {
                'socketId': socket_id,
                'userId': user_id,
                'whiteboardId': whiteboard_id,
            },
        )

    @socketio.on('update_whiteboard')
    def socketio_update_whiteboard(data):
        socket_id = data.get('socketId')
        title = data.get('title')
        users = User.find_by_ids(data.get('userIds'))
        whiteboard_id = data.get('whiteboardId')
        update_whiteboard(
            socket_id=socket_id,
            user=LoginSession(data.get('userId')),
            whiteboard_id=whiteboard_id,
            title=title,
            users=users,
        )
        emit(
            'update_whiteboard',
            {
                'socketId': socket_id,
                'title': title,
                'users': [user.to_api_json() for user in users],
                'whiteboardId': whiteboard_id,
            },
        )

    @socketio.on('update_whiteboard_elements')
    def socketio_update_whiteboard_elements(data):
        socket_id = data.get('socketId')
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        whiteboard_elements = update_whiteboard_elements(
            socket_id=socket_id,
            user=LoginSession(user_id),
            whiteboard_id=whiteboard_id,
            whiteboard_elements=data.get('whiteboardElements', []),
        )
        emit(
            'update_whiteboard',
            {
                'socketId': socket_id,
                'whiteboardElements': [e.to_api_json() for e in whiteboard_elements],
                'whiteboardId': whiteboard_id,
            },
        )

    @socketio.on('add')
    def socketio_add(data):
        socket_id = data.get('socketId')
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        whiteboard_elements = create_whiteboard_elements(
            socket_id=socket_id,
            user=LoginSession(user_id),
            whiteboard_id=whiteboard_id,
            whiteboard_elements=data.get('whiteboardElements', []),
        )
        emit(
            'add',
            {
                'socketId': socket_id,
                'whiteboardElements': [e.to_api_json() for e in whiteboard_elements],
                'whiteboardId': whiteboard_id,
            },
        )
        return whiteboard_elements

    @socketio.on('delete')
    def socketio_delete(data):
        socket_id = data.get('socketId')
        whiteboard_elements = data.get('whiteboardElements', [])
        whiteboard_id = data.get('whiteboardId')
        delete_whiteboard_elements(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=whiteboard_id,
            whiteboard_elements=whiteboard_elements,
        )
        emit(
            'delete',
            {
                'socketId': socket_id,
                'whiteboardElementUids': [e['element']['uuid'] for e in whiteboard_elements],
                'whiteboardId': whiteboard_id,
            },
        )

    @socketio.on('ping')
    def socketio_ping(data):
        return update_updated_at(
            socket_id=data.get('socketId'),
            user_id=data.get('userId'),
            whiteboard_id=data.get('whiteboardId'),
        )

    @socketio.on('disconnect')
    def socketio_disconnect(data):
        print(data)
        pass
