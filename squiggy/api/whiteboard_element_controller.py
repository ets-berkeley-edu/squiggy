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

from flask import current_app as app, request
from flask_login import current_user, login_required
from flask_socketio import emit
from squiggy.api.api_util import feature_flag_whiteboards, get_socket_io_room
from squiggy.lib.errors import BadRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import is_student
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession


@app.route('/api/<whiteboard_id>/element/<uuid>/create', methods=['POST'])
@feature_flag_whiteboards
@login_required
def create_whiteboard_element():
    pass


@app.route('/api/whiteboard/<whiteboard_id>/element/<uuid>/delete', methods=['DELETE'])
@feature_flag_whiteboards
@login_required
def delete_whiteboard_element(whiteboard_id, uuid):
    params = request.args
    socket_id = params.get('socketId')
    if not socket_id:
        raise BadRequestError('socket_id is required')

    whiteboard_element = WhiteboardElement.find_by_uuid(uuid=uuid, whiteboard_id=whiteboard_id)
    if whiteboard_element:
        emit(
            'delete_whiteboard_element',
            uuid,
            include_self=False,
            namespace='/',
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
        if whiteboard_element.asset_id:
            AssetWhiteboardElement.delete(
                asset_id=whiteboard_element.asset_id,
                uuid=whiteboard_element.uuid,
            )
        WhiteboardElement.delete(uuid=uuid, whiteboard_id=whiteboard_id)
        WhiteboardHousekeeping.queue_for_preview_image(whiteboard_id)
        if is_student(current_user):
            WhiteboardSession.update_updated_at(
                socket_id=socket_id,
                user_id=current_user.user_id,
                whiteboard_id=whiteboard_id,
            )
    return tolerant_jsonify(uuid)


@app.route('/api/<whiteboard_id>/element/<uuid>/update', methods=['POST'])
@feature_flag_whiteboards
@login_required
def update_whiteboard_element():
    pass
