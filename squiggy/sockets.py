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

from flask_socketio import emit, send
from squiggy.api.api_whiteboard_util import create_whiteboard_elements, delete_whiteboard_elements, \
    join_whiteboard, leave_whiteboard, update_updated_at, update_whiteboard_elements
from squiggy.lib.login_session import LoginSession


def register_sockets(socketio):

    @socketio.on('join')
    def socketio_join(data):
        api_json = join_whiteboard(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
        )
        emit('join', api_json)
        send(api_json, json=True)

    @socketio.on('leave')
    def socketio_leave(data):
        api_json = leave_whiteboard(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
        )
        emit('leave', api_json)
        send(api_json, json=True)

    @socketio.on('update')
    def socketio_update(data):
        whiteboard_elements = update_whiteboard_elements(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
            whiteboard_elements=data.get('whiteboardElements', []),
        )
        return [e.to_api_json() for e in whiteboard_elements]

    @socketio.on('add')
    def socketio_add(data):
        whiteboard_elements = create_whiteboard_elements(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
            whiteboard_elements=data.get('whiteboardElements', []),
        )
        return [e.to_api_json() for e in whiteboard_elements]

    @socketio.on('delete')
    def socketio_delete(data):
        delete_whiteboard_elements(
            socket_id=data.get('socketId'),
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
            whiteboard_elements=data.get('whiteboardElements', []),
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
