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
from squiggy.api.api_util import can_update_whiteboard, can_view_whiteboard, feature_flag_whiteboards
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import local_now
from squiggy.lib.whiteboard_util import is_ready_to_export, to_png_file
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
    whiteboard = _find_whiteboard(whiteboard_id=whiteboard_id)
    if whiteboard and can_view_whiteboard(user=current_user, whiteboard=whiteboard):
        socket_id = request.args.get('socketId')
        if socket_id:
            WhiteboardSession.create(
                socket_id=socket_id,
                user_id=current_user.get_id(),
                whiteboard_id=whiteboard_id,
            )
        return tolerant_jsonify(whiteboard)
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboard/<whiteboard_id>/export/asset', methods=['POST'])
@feature_flag_whiteboards
@login_required
def export_as_asset(whiteboard_id):
    whiteboard = _find_whiteboard(whiteboard_id)
    if whiteboard and can_view_whiteboard(user=current_user, whiteboard=whiteboard):
        whiteboard_elements = WhiteboardElement.find_by_whiteboard_id(whiteboard_id=whiteboard_id)
        if whiteboard_elements:
            params = request.get_json()
            category_ids = list(params.get('categoryIds'))
            description = params.get('description')
            title = params.get('title') or whiteboard['title']
            asset = Asset.create(
                asset_type='whiteboard',
                canvas_assignment_id=None,
                categories=[Category.find_by_id(category_id=category_id) for category_id in category_ids],
                course_id=current_user.course.id,
                create_activity=True,
                description=description,
                download_url=whiteboard['imageUrl'],
                mime=None,
                source=str(whiteboard['id']),
                title=title,
                url=None,
                users=[User.find_by_id(current_user.get_id())],
                visible=True,
            )
            for whiteboard_element in whiteboard_elements:
                element = whiteboard_element.element
                AssetWhiteboardElement.create(
                    asset_id=asset.id,
                    element=element,
                    element_asset_id=element.get('assetId'),
                    uuid=element['uuid'],
                )
            return tolerant_jsonify(Asset.find_by_id(asset_id=asset.id).to_api_json())
        else:
            raise BadRequestError('An empty whiteboard cannot be exported')
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboard/<whiteboard_id>/export/png')
@feature_flag_whiteboards
@login_required
def export_as_png(whiteboard_id):
    whiteboard = _find_whiteboard(whiteboard_id)
    if not whiteboard:
        raise ResourceNotFoundError('Not found')
    if not can_view_whiteboard(user=current_user, whiteboard=whiteboard):
        raise BadRequestError('Unauthorized')
    if not is_ready_to_export(whiteboard_id):
        raise BadRequestError('Whiteboard cannot be converted to PNG until previews are generated. Try again soon.')
    # Download
    now = local_now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = re.sub(r'[^a-zA-Z0-9]', '_', whiteboard['title'])
    return send_file(
        as_attachment=True,
        attachment_filename=f'{filename}_{now}.png',
        path_or_file=to_png_file(whiteboard),
    )


@app.route('/api/whiteboard/<whiteboard_id>/restore')
@feature_flag_whiteboards
@login_required
def restore_whiteboard(whiteboard_id):
    whiteboard = _find_whiteboard(whiteboard_id)
    if whiteboard and can_update_whiteboard(user=current_user, whiteboard=whiteboard):
        restored = Whiteboard.restore(whiteboard_id)
        return tolerant_jsonify(restored.to_api_json())
    else:
        raise ResourceNotFoundError('Not found')


@app.route('/api/whiteboards', methods=['POST'])
@feature_flag_whiteboards
@login_required
def get_whiteboards():
    params = request.get_json()
    include_deleted = params.get('includeDeleted', False) if current_user.is_admin else False
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
    params = request.get_json() or request.form
    title = params.get('title')
    user_ids = params.get('userIds')
    whiteboard = Whiteboard.create(
        course_id=current_user.course.id,
        title=title,
        users=User.find_by_ids(user_ids),
    )
    return tolerant_jsonify(whiteboard)


@app.route('/api/whiteboard/<whiteboard_id>/delete', methods=['DELETE'])
@feature_flag_whiteboards
@login_required
def delete_whiteboard(whiteboard_id):
    whiteboard = _find_whiteboard(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Not found')
    if not can_update_whiteboard(user=current_user, whiteboard=whiteboard):
        raise BadRequestError('To delete this asset you must own it or be a teacher or admin in the course.')
    whiteboard_id = whiteboard['id']
    Whiteboard.delete(whiteboard_id=whiteboard_id)
    return tolerant_jsonify({'message': f'Whiteboard {whiteboard_id} deleted'}), 200


@app.route('/api/whiteboard/update', methods=['POST'])
@feature_flag_whiteboards
@login_required
def update_whiteboard():
    params = request.get_json()
    whiteboard_id = params.get('whiteboardId')
    title = params.get('title')
    user_ids = params.get('userIds')
    whiteboard = _find_whiteboard(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Not found')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not can_update_whiteboard(user=current_user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')

    whiteboard = Whiteboard.update(
        whiteboard_id=whiteboard_id,
        title=title,
        users=User.find_by_ids(user_ids),
    )
    return tolerant_jsonify(whiteboard.to_api_json())


def _find_whiteboard(whiteboard_id):
    return Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
