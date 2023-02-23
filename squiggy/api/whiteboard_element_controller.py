"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from squiggy.api.api_util import get_socket_io_room, upsert_whiteboard_elements
from squiggy.lib.errors import BadRequestError, UnauthorizedRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.logger import logger
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession
from squiggy.sockets import SOCKET_IO_NAMESPACE


@app.route('/api/whiteboard_elements/order', methods=['POST'])
@login_required
def order_whiteboard_elements():
    params = request.form or request.get_json()
    direction = params.get('direction')
    socket_id = params.get('socketId')
    uuids = params.get('uuids')
    whiteboard_id = params.get('whiteboardId')
    if not Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        raise UnauthorizedRequestError('Unauthorized')
    if not direction:
        raise BadRequestError('direction is required')
    if not socket_id:
        raise BadRequestError('socket_id is required')
    if len(uuids or []) == 0:
        raise BadRequestError('uuids required')

    # Order the whiteboard_elements
    WhiteboardElement.update_z_indexes(
        direction=direction,
        uuids=uuids,
        whiteboard_id=whiteboard_id,
    )

    if not app.config['TESTING']:
        logger.info(f'socketio: Emit order_whiteboard_elements where uuids = {uuids}')
        emit(
            'order_whiteboard_elements',
            {
                'direction': direction,
                'uuids': uuids,
            },
            include_self=False,
            namespace=SOCKET_IO_NAMESPACE,
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
    WhiteboardSession.update_updated_at(
        socket_id=socket_id,
        user_id=current_user.user_id,
        whiteboard_id=whiteboard_id,
    )
    return tolerant_jsonify({'message': 'Success'})


@app.route('/api/whiteboard_elements/upsert', methods=['POST'])
@login_required
def upsert():
    params = request.form or request.get_json()
    socket_id = params.get('socketId')
    whiteboard_elements = params.get('whiteboardElements')
    whiteboard_id = params.get('whiteboardId')

    results = upsert_whiteboard_elements(
        socket_id=socket_id,
        whiteboard_elements=whiteboard_elements,
        whiteboard_id=whiteboard_id,
    )
    return tolerant_jsonify(results)


@app.route('/api/whiteboard_elements/delete', methods=['DELETE'])
@login_required
def delete_whiteboard_elements():
    params = request.form or request.get_json()
    socket_id = params.get('socketId')
    uuids = params.get('uuids')
    whiteboard_id = params.get('whiteboardId')
    if not socket_id:
        raise BadRequestError('socket_id is required')
    if not Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        raise UnauthorizedRequestError('Unauthorized')

    whiteboard_elements = WhiteboardElement.find_all(uuids=uuids, whiteboard_id=whiteboard_id)
    if len(whiteboard_elements):
        logger.info(f'socketio: Emit delete_whiteboard_elements where whiteboard_id = {whiteboard_id}')
        for whiteboard_element in whiteboard_elements:
            if whiteboard_element.asset_id:
                AssetWhiteboardElement.delete(
                    asset_id=whiteboard_element.asset_id,
                    uuid=whiteboard_element.uuid,
                )
        if not app.config['TESTING']:
            emit(
                'delete_whiteboard_elements',
                uuids,
                include_self=False,
                namespace=SOCKET_IO_NAMESPACE,
                skip_sid=socket_id,
                to=get_socket_io_room(whiteboard_id),
            )
        WhiteboardElement.delete_all(uuids=uuids, whiteboard_id=whiteboard_id)
        WhiteboardHousekeeping.queue_for_preview_image(whiteboard_id)
        WhiteboardSession.update_updated_at(
            socket_id=socket_id,
            user_id=current_user.user_id,
            whiteboard_id=whiteboard_id,
        )
    return tolerant_jsonify(uuids)
