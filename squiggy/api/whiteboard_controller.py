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
from squiggy.api.api_util import can_update_whiteboard, can_view_whiteboard
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import Asset
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.category import Category
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession

# TODO
# GET: '/whiteboard/<whiteboard_id>/export/png',
# POST: '/whiteboards/<whiteboard_id>/restore',


@app.route('/api/whiteboard/<whiteboard_id>')
@login_required
def get_whiteboard(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(whiteboard_id=whiteboard_id)
    if whiteboard and can_view_whiteboard(user=current_user, whiteboard=whiteboard):
        socket_id = request.args.get('socketId')
        if socket_id:
            WhiteboardSession.upsert(
                socket_id=socket_id,
                user_id=current_user.get_id(),
                whiteboard_id=whiteboard_id,
            )
        return tolerant_jsonify(whiteboard)
    else:
        raise ResourceNotFoundError(f'No asset found with id: {whiteboard_id}')


@app.route('/api/whiteboard/<whiteboard_id>/export/asset', methods=['POST'])
@login_required
def export_as_asset(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(whiteboard_id=whiteboard_id)
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
            AssetWhiteboardElement.create(asset_id=asset.id, whiteboard_elements=whiteboard_elements)
            return tolerant_jsonify(Asset.find_by_id(asset_id=asset.id).to_api_json())
        else:
            raise BadRequestError('An empty whiteboard cannot be exported')
    else:
        raise ResourceNotFoundError(f'No asset found with id: {whiteboard_id}')


@app.route('/api/whiteboards', methods=['POST'])
@login_required
def get_whiteboards():
    params = request.get_json()
    include_deleted = params.get('includeDeleted', False)
    limit = params.get('limit')
    offset = params.get('offset')
    order_by = params.get('orderBy') or 'recent'
    return tolerant_jsonify(Whiteboard.get_whiteboards(
        course_id=current_user.course.id,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
        order_by=order_by,
    ))


@app.route('/api/whiteboard/create', methods=['POST'])
@login_required
def create_whiteboard():
    if not current_user.course:
        raise BadRequestError('Course data not found')
    params = request.get_json() or request.form
    title = params.get('title')
    user_ids = params.get('userIds')
    if not title or not user_ids:
        raise BadRequestError('Title is required.')

    whiteboard = Whiteboard.create(
        course_id=current_user.course.id,
        title=title,
        users=User.find_by_ids(user_ids),
    )
    return tolerant_jsonify(whiteboard.to_api_json())


@app.route('/api/whiteboard/<whiteboard_id>/delete', methods=['DELETE'])
@login_required
def delete_whiteboard(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if not can_update_whiteboard(user=current_user, whiteboard=whiteboard):
        raise BadRequestError('To delete this asset you must own it or be a teacher or admin in the course.')
    whiteboard_id = whiteboard['id']
    Whiteboard.delete(whiteboard_id=whiteboard_id)
    return tolerant_jsonify({'message': f'Whiteboard {whiteboard_id} deleted'}), 200


@app.route('/api/whiteboard/update', methods=['POST'])
@login_required
def update_whiteboard():
    params = request.get_json()
    whiteboard_id = params.get('whiteboardId')
    title = params.get('title')
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard or not title:
        raise BadRequestError('Whiteboard update requires a valid ID and title.')
    if not can_update_whiteboard(user=current_user, whiteboard=whiteboard):
        raise BadRequestError('To update an asset you must own it or be a teacher in the course.')

    whiteboard = Whiteboard.update(whiteboard_id=whiteboard_id, title=title)
    return tolerant_jsonify(whiteboard.to_api_json(user_id=current_user.get_id()))


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value
