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

import re

from flask import current_app as app, request, send_file
from flask_login import current_user, login_required
from flask_socketio import emit
from squiggy.api.api_util import can_view_asset, feature_flag_whiteboards, get_socket_io_room, SOCKET_IO_NAMESPACE
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import is_student, isoformat, local_now
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.lib.whiteboard_util import to_png_file
from squiggy.logger import logger
from squiggy.models.asset import Asset
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.category import Category
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession


@app.route('/api/whiteboard/<whiteboard_id>')
@feature_flag_whiteboards
@login_required
def get_whiteboard(whiteboard_id):
    if Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        whiteboard = Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
        return tolerant_jsonify(whiteboard)
    else:
        raise ResourceNotFoundError('Whiteboard not found')


@app.route('/api/whiteboard/remix', methods=['POST'])
@feature_flag_whiteboards
@login_required
def remix_whiteboard():
    params = request.get_json()
    asset_id = params.get('assetId')
    title = params.get('title')
    asset = Asset.find_by_id(asset_id=asset_id)
    print(asset)
    if not asset or not can_view_asset(asset=asset, user=current_user):
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')
    if asset.asset_type != 'whiteboard':
        raise BadRequestError('Asset type is not \'whiteboard\'.')
    if not (title or '').strip():
        raise BadRequestError('title is required')
    whiteboard = Whiteboard.remix(
        asset_id=asset.id,
        course_id=asset.course_id,
        created_by=User.find_by_id(current_user.user_id),
        title=title,
        whiteboard_users=asset.users,
    )
    WhiteboardHousekeeping.queue_for_preview_image(whiteboard['id'])
    return tolerant_jsonify(Whiteboard.find_by_id(current_user, whiteboard_id=whiteboard['id']))


@app.route('/api/whiteboard/<whiteboard_id>/export/asset', methods=['POST'])
@feature_flag_whiteboards
@login_required
def export_as_asset(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
    if whiteboard:
        whiteboard_elements = WhiteboardElement.find_by_whiteboard_id(whiteboard_id=whiteboard_id)
        if whiteboard_elements:
            params = request.get_json()
            category_ids = list(params.get('categoryIds', []))
            description = params.get('description')
            title = params.get('title') or whiteboard['title']
            if not title:
                raise BadRequestError('Required parameter is missing.')
            collaborator_user_ids = [u['id'] for u in whiteboard['users']]
            asset = Asset.create(
                asset_type='whiteboard',
                categories=[Category.find_by_id(category_id=category_id) for category_id in category_ids],
                course_id=current_user.course.id,
                created_by=current_user.user_id,
                description=description,
                download_url=whiteboard['imageUrl'],
                source=str(whiteboard['id']),
                title=title,
                users=User.find_by_ids(collaborator_user_ids),
            )
            for whiteboard_element in whiteboard_elements:
                element = whiteboard_element.element
                AssetWhiteboardElement.create(
                    asset_id=asset.id,
                    element=element,
                    element_asset_id=element.get('assetId'),
                    uuid=element['uuid'],
                    z_index=whiteboard_element.z_index,
                )
            return tolerant_jsonify(Asset.find_by_id(asset_id=asset.id).to_api_json())
        else:
            raise BadRequestError('An empty whiteboard cannot be exported')
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboard/<whiteboard_id>/download/png')
@feature_flag_whiteboards
@login_required
def export_as_png(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
    if not whiteboard:
        raise ResourceNotFoundError('Not found')

    key = 'assetPreviewStatus'
    asset_preview_statuses = [e[key] for e in whiteboard['whiteboardElements'] if key in e]
    if 'error' in asset_preview_statuses:
        raise BadRequestError('Whiteboard cannot be exported due to an asset processing error. Remove problematic assets and retry.')
    if 'pending' in asset_preview_statuses:
        raise BadRequestError('Whiteboard cannot be exported yet, assets are still processing. Try again soon.')

    # Download
    now = local_now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = re.sub(r'[^a-zA-Z0-9]', '_', whiteboard['title'])
    png_file = to_png_file(whiteboard)
    if png_file:
        return send_file(
            as_attachment=True,
            attachment_filename=f'{filename}_{now}.png',
            path_or_file=png_file.name,
        )
    else:
        raise BadRequestError('Failed to generate whiteboard PNG')


@app.route('/api/whiteboard/<whiteboard_id>/undelete', methods=['POST'])
@feature_flag_whiteboards
@login_required
def undelete_whiteboard(whiteboard_id):
    if Whiteboard.can_update_whiteboard(include_deleted=True, current_user=current_user, whiteboard_id=whiteboard_id):
        params = request.get_json()
        socket_id = params.get('socketId')
        if not socket_id:
            # Socket ID is required because delete can only happen in context of a /whiteboard session.
            raise BadRequestError('socket_id is required')
        # Restore the whiteboard
        whiteboard = Whiteboard.undelete(whiteboard_id)
        # Broadcast via socket.io
        if not app.config['TESTING']:
            logger.info(f'socketio: Emit update_whiteboard where whiteboard_id = {whiteboard_id}')
            emit(
                'update_whiteboard',
                {
                    'deletedAt': isoformat(whiteboard.deleted_at),
                    'title': whiteboard.title,
                    'users': whiteboard.users,
                    'whiteboardId': whiteboard.id,
                },
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
        return tolerant_jsonify(whiteboard.to_api_json())
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboards', methods=['POST'])
@feature_flag_whiteboards
@login_required
def get_whiteboards():
    params = request.get_json()
    include_deleted = params.get('includeDeleted', False) if current_user.is_admin or current_user.is_teaching else False
    keywords = params.get('keywords')
    limit = params.get('limit')
    offset = params.get('offset')
    order_by = params.get('orderBy') or 'recent'
    user_id = params.get('userId')
    summary = Whiteboard.get_whiteboards(
        course_id=current_user.course.id,
        current_user=current_user,
        include_deleted=include_deleted,
        keywords=keywords,
        limit=limit,
        offset=offset,
        order_by=order_by,
        user_id=user_id,
    )
    return tolerant_jsonify(summary)


@app.route('/api/whiteboard/create', methods=['POST'])
@feature_flag_whiteboards
@login_required
def create_whiteboard():
    if not current_user.course:
        raise ResourceNotFoundError('Course not found.')
    params = request.form or request.get_json()
    title = params.get('title')
    user_ids = params.get('userIds')
    whiteboard = Whiteboard.create(
        course_id=current_user.course.id,
        created_by=current_user.user_id,
        title=title,
        users=User.find_by_ids(user_ids),
    )
    return tolerant_jsonify(whiteboard)


@app.route('/api/whiteboard/<whiteboard_id>/delete', methods=['DELETE'])
@feature_flag_whiteboards
@login_required
def delete_whiteboard(whiteboard_id):
    if Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        params = request.args
        socket_id = params.get('socketId')
        if not socket_id:
            # Socket ID is required because delete can only happen in context of a /whiteboard session.
            raise BadRequestError('socket_id is required')
        # Delete
        whiteboard = Whiteboard.delete(whiteboard_id=whiteboard_id)
        # Broadcast via socket.io
        if not app.config['TESTING']:
            logger.info(f'socketio: Emit update_whiteboard where whiteboard_id = {whiteboard_id}')
            emit(
                'update_whiteboard',
                {
                    'deletedAt': isoformat(whiteboard.deleted_at),
                    'title': whiteboard.title,
                    'users': [user.to_api_json() for user in whiteboard.users],
                    'whiteboardId': whiteboard.id,
                },
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
        return tolerant_jsonify({'message': f'Whiteboard {whiteboard_id} deleted'}), 200
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboards/eligible_collaborators')
@login_required
def eligible_collaborators():
    course_id = current_user.course.id
    sections = current_user.user.canvas_course_sections if current_user.is_student and current_user.course.protects_assets_per_section else None
    return tolerant_jsonify([u.to_api_json() for u in User.get_users_by_course_id(course_id=course_id, sections=sections)])


@app.route('/api/whiteboard/<whiteboard_id>/update', methods=['POST'])
@feature_flag_whiteboards
@login_required
def update_whiteboard(whiteboard_id):
    if Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        params = request.get_json()
        socket_id = params.get('socketId')
        title = params.get('title')
        user_ids = params.get('userIds')
        if not socket_id:
            # Socket ID is required because update can only happen in context of a /whiteboard session.
            raise BadRequestError('socket_id is required')
        # Update
        whiteboard = Whiteboard.update(
            whiteboard_id=whiteboard_id,
            title=title,
            users=User.find_by_ids(user_ids),
        )
        whiteboard = whiteboard.to_api_json()
        # Broadcast via socket.io
        if not app.config['TESTING']:
            logger.info(f'socketio: Emit update_whiteboard where whiteboard_id = {whiteboard_id}')
            emit(
                'update_whiteboard',
                {
                    'deletedAt': whiteboard['deletedAt'],
                    'title': whiteboard['title'],
                    'users': whiteboard['users'],
                    'whiteboardId': whiteboard['id'],
                },
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
        return tolerant_jsonify(whiteboard)
    else:
        raise ResourceNotFoundError('Not found')
