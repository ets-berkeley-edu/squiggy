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

from flask import current_app as app
from flask_socketio import join_room, leave_room
from squiggy.api.api_util import can_update_whiteboard
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.util import safe_strip
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession


def create_whiteboard_elements(socket_id, user, whiteboard_id, whiteboard_elements):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not len(whiteboard_elements):
        raise BadRequestError('One or more whiteboard-elements required')
    if not can_update_whiteboard(user=user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')

    def _create(whiteboard_element):
        _validate_whiteboard_element(whiteboard_element)
        return WhiteboardElement.create(
            asset_id=whiteboard_element.get('assetId', None),
            element=whiteboard_element['element'],
            whiteboard_id=whiteboard_id,
        )
    results = [_create(whiteboard_element) for whiteboard_element in whiteboard_elements]
    update_updated_at(
        socket_id=socket_id,
        user_id=user.user_id,
        whiteboard_id=whiteboard_id,
    )
    return results


def delete_whiteboard_elements(socket_id, user, whiteboard_id, whiteboard_elements):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not len(whiteboard_elements):
        raise BadRequestError('One or more whiteboard-elements required')
    if not can_update_whiteboard(user=user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')

    for whiteboard_element in whiteboard_elements:
        WhiteboardElement.delete(uuid=whiteboard_element['element']['uuid'], whiteboard_id=whiteboard_id)
    update_updated_at(
        socket_id=socket_id,
        user_id=user.user_id,
        whiteboard_id=whiteboard_id,
    )


def join_whiteboard(socket_id, user, whiteboard_id):
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id).first()
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    join_room(whiteboard)
    # Delete stale sessions
    WhiteboardSession.delete_stale_records(older_than_minutes=10)
    for session in WhiteboardSession.find(user_id=user.user_id, whiteboard_id=whiteboard_id):
        WhiteboardSession.delete(session.socket_id)
    # Create
    return update_updated_at(
        socket_id=socket_id,
        user_id=user.user_id,
        whiteboard_id=whiteboard_id,
    )


def leave_whiteboard(socket_id, user, whiteboard_id):
    whiteboard = Whiteboard.query.filter_by(id=whiteboard_id).first()
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    leave_room(whiteboard)
    WhiteboardSession.delete(socket_id)


def update_updated_at(socket_id, user_id, whiteboard_id):
    if WhiteboardSession.find_by_socket_id(socket_id=socket_id):
        WhiteboardSession.update_updated_at(socket_id=socket_id)
    else:
        WhiteboardSession.create(
            socket_id=socket_id,
            user_id=user_id,
            whiteboard_id=whiteboard_id,
        )
    return Whiteboard.get_active_collaborators(whiteboard_id=whiteboard_id)


def update_whiteboard(socket_id, title, user, users, whiteboard_id):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not can_update_whiteboard(user=user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')

    whiteboard = Whiteboard.update(
        title=title,
        users=users,
        whiteboard_id=whiteboard_id,
    )
    update_updated_at(
        socket_id=socket_id,
        user_id=user.user_id,
        whiteboard_id=whiteboard_id,
    )
    return whiteboard.to_api_json()


def update_whiteboard_elements(socket_id, user, whiteboard_id, whiteboard_elements):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not len(whiteboard_elements):
        raise BadRequestError('One or more elements required')
    if not can_update_whiteboard(user=user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')

    def _update(whiteboard_element):
        _validate_whiteboard_element(whiteboard_element, True)
        element = whiteboard_element['element']
        whiteboard_element = WhiteboardElement.update(
            asset_id=whiteboard_element.get('assetId', None),
            element=element,
            uuid=element['uuid'],
            whiteboard_id=whiteboard_id,
        )
        if not whiteboard_element:
            raise BadRequestError('Whiteboard element not found')
        return whiteboard_element
    results = [_update(whiteboard_element) for whiteboard_element in whiteboard_elements]
    update_updated_at(
        socket_id=socket_id,
        user_id=user.user_id,
        whiteboard_id=whiteboard_id,
    )
    return results


def _validate_whiteboard_element(whiteboard_element, is_update=False):
    element = whiteboard_element['element']
    error_message = None
    if element['type'] == 'i-text' and not safe_strip(element.get('text')):
        error_message = f'Invalid Fabric i-text element: {element}.'
    if is_update:
        if 'uuid' not in element:
            error_message = 'uuid is required when updating existing whiteboard_element.'
    elif element.get('uuid'):
        error_message = 'A new whiteboard_element cannot have a defined \'uuid\'.'
    if error_message:
        app.logger.error(error_message)
        raise BadRequestError(error_message)
