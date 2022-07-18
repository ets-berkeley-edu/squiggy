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
from squiggy.lib.errors import BadRequestError, UnauthorizedRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import is_student, safe_strip
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.logger import logger
from squiggy.models.activity import Activity
from squiggy.models.asset import Asset
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession
from squiggy.sockets import SOCKET_IO_NAMESPACE


@app.route('/api/whiteboard_elements/order', methods=['POST'])
@feature_flag_whiteboards
@login_required
def order_whiteboard_elements():
    params = request.form or request.get_json()
    socket_id = params.get('socketId')
    uuids = params.get('uuids')
    whiteboard_id = params.get('whiteboardId')
    if not Whiteboard.can_update_whiteboard(user=current_user, whiteboard_id=whiteboard_id):
        raise UnauthorizedRequestError('Unauthorized')
    if not socket_id:
        raise BadRequestError('socket_id is required')
    if len(uuids or []) == 0:
        raise BadRequestError('uuids required')

    # Order the whiteboard_elements
    WhiteboardElement.update_order(uuids=uuids, whiteboard_id=whiteboard_id)

    if not app.config['TESTING']:
        logger.info(f'socketio: Emit order_whiteboard_elements where uuids = {uuids}')
        emit(
            'order_whiteboard_elements',
            uuids,
            include_self=False,
            namespace=SOCKET_IO_NAMESPACE,
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
    if is_student(current_user):
        WhiteboardSession.update_updated_at(
            socket_id=socket_id,
            user_id=current_user.user_id,
            whiteboard_id=whiteboard_id,
        )
    return tolerant_jsonify(uuids)


@app.route('/api/whiteboard_elements/upsert', methods=['POST'])
@feature_flag_whiteboards
@login_required
def upsert_whiteboard_elements():
    params = request.form or request.get_json()
    socket_id = params.get('socketId')
    whiteboard_elements = params.get('whiteboardElements')
    whiteboard_id = params.get('whiteboardId')
    if not Whiteboard.can_update_whiteboard(user=current_user, whiteboard_id=whiteboard_id):
        raise UnauthorizedRequestError('Unauthorized')
    if not socket_id:
        raise BadRequestError('socket_id is required')

    results = []
    for whiteboard_element in whiteboard_elements:
        results.append(
            _upsert_whiteboard_element(
                socket_id=socket_id,
                whiteboard_id=whiteboard_id,
                whiteboard_element=whiteboard_element,
            ),
        )
    if not app.config['TESTING']:
        logger.info(f'socketio: Emit upsert_whiteboard_elements where whiteboard_id = {whiteboard_id} AND socket_id = {socket_id}')
        emit(
            'upsert_whiteboard_elements',
            whiteboard_elements,
            include_self=False,
            namespace=SOCKET_IO_NAMESPACE,
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
    if is_student(current_user):
        WhiteboardSession.update_updated_at(
            socket_id=socket_id,
            user_id=current_user.user_id,
            whiteboard_id=whiteboard_id,
        )
    return tolerant_jsonify(results)


@app.route('/api/whiteboard/<whiteboard_id>/element/<uuid>/delete', methods=['DELETE'])
@feature_flag_whiteboards
@login_required
def delete_whiteboard_element(whiteboard_id, uuid):
    params = request.args
    socket_id = params.get('socketId')
    if not socket_id:
        raise BadRequestError('socket_id is required')

    whiteboard_element = WhiteboardElement.find_by_uuid(uuid=uuid, whiteboard_id=whiteboard_id)
    if whiteboard_element and not app.config['TESTING']:
        logger.info(f'socketio: Emit delete_whiteboard_element where whiteboard_id = {whiteboard_id} AND socket_id = {socket_id}')
        emit(
            'delete_whiteboard_element',
            uuid,
            include_self=False,
            namespace=SOCKET_IO_NAMESPACE,
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


def _create_whiteboard_element(whiteboard_element, whiteboard_id):
    if not whiteboard_element:
        raise BadRequestError('Whiteboard element required')

    _validate_whiteboard_element(whiteboard_element)
    asset_id = whiteboard_element.get('assetId')
    element = whiteboard_element['element']
    whiteboard_element = WhiteboardElement.create(
        asset_id=asset_id,
        element=element,
        uuid=element['uuid'],
        whiteboard_id=whiteboard_id,
    )
    if asset_id:
        AssetWhiteboardElement.upsert(
            asset_id=asset_id,
            element=element,
            element_asset_id=element.get('assetId'),
            uuid=element['uuid'],
        )
        asset = Asset.find_by_id(asset_id)
        user_id = current_user.user_id
        if user_id not in [user.id for user in asset.users]:
            course_id = current_user.course.id
            Activity.create(
                activity_type='whiteboard_add_asset',
                course_id=course_id,
                user_id=user_id,
                object_type='whiteboard',
                object_id=whiteboard_id,
                asset_id=asset.id,
            )
            for asset_user in asset.users:
                Activity.create(
                    activity_type='get_whiteboard_add_asset',
                    course_id=course_id,
                    user_id=asset_user.id,
                    object_type='whiteboard',
                    object_id=whiteboard_id,
                    asset_id=asset.id,
                )
    return whiteboard_element.to_api_json()


def _upsert_whiteboard_element(socket_id, whiteboard_element, whiteboard_id):
    if WhiteboardElement.get_id_per_uuid(whiteboard_element['uuid']):
        whiteboard_element = _update_whiteboard_element(
            whiteboard_element=whiteboard_element,
            whiteboard_id=whiteboard_id,
        )
    else:
        whiteboard_element = _create_whiteboard_element(
            whiteboard_element=whiteboard_element,
            whiteboard_id=whiteboard_id,
        )
    WhiteboardHousekeeping.queue_for_preview_image(whiteboard_id)
    return whiteboard_element


def _update_whiteboard_element(whiteboard_element, whiteboard_id):
    if not whiteboard_element:
        raise BadRequestError('Element required')

    _validate_whiteboard_element(whiteboard_element, True)

    element = whiteboard_element['element']
    result = WhiteboardElement.update(
        asset_id=whiteboard_element.get('assetId'),
        element=element,
        uuid=element['uuid'],
        whiteboard_id=whiteboard_id,
    )
    return result.to_api_json()


def _validate_whiteboard_element(whiteboard_element, is_update=False):
    element = whiteboard_element['element']
    error_message = None
    if element['type'] == 'i-text' and not safe_strip(element.get('text')):
        error_message = f'Invalid Fabric i-text element: {element}.'
    if is_update:
        if 'uuid' not in element:
            error_message = 'uuid is required when updating existing whiteboard_element.'
    if error_message:
        app.logger.error(error_message)
        raise BadRequestError(error_message)
