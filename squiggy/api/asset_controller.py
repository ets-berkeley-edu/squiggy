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

import json
import re

from flask import current_app as app, request, Response
from flask_login import current_user, login_required
from squiggy.api.api_util import can_update_asset, can_view_asset
from squiggy.lib.aws import stream_object, upload_to_s3
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import retrieve_to_file, tolerant_jsonify
from squiggy.lib.previews import get_s3_key_prefix
from squiggy.lib.util import is_admin, is_teaching, local_now, to_bool_or_none
from squiggy.models.asset import Asset, validate_asset_url
from squiggy.models.category import Category
from squiggy.models.user import User


@app.route('/api/asset/<asset_id>/download')
@login_required
def download(asset_id):
    asset = Asset.find_by_id(asset_id)
    s3_url = asset.download_url
    if asset and s3_url and can_view_asset(asset=asset, user=current_user):
        stream = stream_object(s3_url)
        if stream:
            now = local_now().strftime('%Y-%m-%d_%H-%M-%S')
            name = re.sub(r'[^a-zA-Z0-9]', '_', asset.title)
            extension = s3_url.rsplit('.', 1)[-1]
            return Response(
                stream,
                headers={
                    'Content-disposition': f'attachment; filename="{name}_{now}.{extension}"',
                },
            )
    raise ResourceNotFoundError(f'Asset {asset_id} not found.')


@app.route('/api/asset/<asset_id>')
@login_required
def get_asset(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset and can_view_asset(asset=asset, user=current_user):
        if current_user.user not in asset.users:
            asset.increment_views(current_user.user)
        return tolerant_jsonify(asset.to_api_json(user_id=current_user.get_id()))
    else:
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')


@app.route('/api/assets', methods=['POST'])
@login_required
def get_assets():
    params = request.get_json()
    order_by = _get(params, 'orderBy', 'recent')
    offset = params.get('offset')
    limit = params.get('limit')
    filters = {
        'asset_type': _get(params, 'assetType', None),
        'category_id': _get(params, 'categoryId', None),
        'has_comments': (order_by == 'comments'),
        'has_likes': (order_by == 'likes'),
        'has_views': (order_by == 'views'),
        'keywords': _get(params, 'keywords', None),
        'owner_id': _get(params, 'userId', None),
        'section': _get(params, 'section', None),
    }
    results = Asset.get_assets(session=current_user, order_by=order_by, offset=offset, limit=limit, filters=filters)
    return tolerant_jsonify(results)


@app.route('/api/asset/create', methods=['POST'])
@login_required
def create_asset():
    params = request.form or request.get_json()
    asset_type = params.get('type')
    from_bookmarklet = to_bool_or_none(params.get('bookmarklet', False))
    category_id = params.get('categoryId')
    description = params.get('description')
    source = params.get('source')
    url = params.get('url')
    title = params.get('title', url)
    visible = to_bool_or_none(params.get('visible', True))
    if not asset_type or not title:
        raise BadRequestError('Asset creation requires title and type.')

    if asset_type == 'link':
        if not url:
            raise BadRequestError('Link asset creation requires url.')
        url_error = validate_asset_url(url)
        if url_error:
            raise BadRequestError(url_error)

    if not current_user.course:
        raise BadRequestError('Course data not found')

    s3_attrs = {}
    if asset_type == 'file':
        if from_bookmarklet:
            file = retrieve_to_file(url)
            name = url.rsplit('/', 1)[-1]
            for char in ['?', '#']:
                name = name.split(char)[0]
            file_upload = {
                'name': name,
                'byte_stream': file.read(),
            }
        else:
            file_upload = _get_upload_from_http_post()
        s3_attrs = upload_to_s3(
            filename=file_upload['name'],
            byte_stream=file_upload['byte_stream'],
            s3_key_prefix=get_s3_key_prefix(current_user.course.id, 'asset'),
        )

    asset = Asset.create(
        asset_type=asset_type,
        categories=category_id and [Category.find_by_id(category_id)],
        course_id=current_user.course.id,
        created_by=current_user.user_id,
        description=description,
        download_url=s3_attrs.get('download_url', None),
        mime=s3_attrs.get('content_type', None),
        source=source,
        title=title,
        url=url,
        users=[User.find_by_id(current_user.get_id())],
        visible=visible,
    )
    return tolerant_jsonify(asset.to_api_json())


@app.route('/api/asset/<asset_id>/delete', methods=['DELETE'])
@login_required
def delete_asset(asset_id):
    asset = Asset.find_by_id(asset_id) if asset_id else None
    if not asset:
        raise ResourceNotFoundError('Asset not found.')
    if not can_update_asset(asset=asset, user=current_user):
        raise BadRequestError('To delete this asset you must own it or be a teacher or admin in the course.')
    if (not is_admin(current_user) and not is_teaching(current_user)) and (asset.comment_count or asset.likes or asset.is_used_in_whiteboards()):
        raise BadRequestError('You cannot delete an asset with comments, likes, or whiteboard usages.')
    Asset.delete(asset_id=asset_id)
    return tolerant_jsonify({'message': f'Asset {asset_id} deleted'}), 200


@app.route('/api/asset/<asset_id>/like', methods=['POST'])
@login_required
def like_asset(asset_id):
    asset = _get_asset_for_like(asset_id)
    asset.add_like(user=current_user)
    return tolerant_jsonify(asset.to_api_json(user_id=current_user.get_id()))


@app.route('/api/asset/<asset_id>/refresh_preview', methods=['POST'])
@login_required
def refresh_preview(asset_id):
    asset = Asset.find_by_id(asset_id) if asset_id else None
    if not asset or asset.asset_type != 'link':
        raise BadRequestError('Preview refresh requires a valid link asset.')
    if not can_update_asset(asset=asset, user=current_user):
        raise BadRequestError('To refresh an asset preview you must own it or be a teacher in the course.')
    asset.refresh_link_preview()
    return tolerant_jsonify(asset.to_api_json(user_id=current_user.get_id()))


@app.route('/api/asset/<asset_id>/remove_like', methods=['POST'])
@login_required
def remove_like_asset(asset_id):
    asset = _get_asset_for_like(asset_id)
    asset.remove_like(user=current_user)
    return tolerant_jsonify(asset.to_api_json(user_id=current_user.get_id()))


@app.route('/api/asset/update', methods=['POST'])
@login_required
def update_asset():
    params = request.get_json()
    asset_id = params.get('assetId')
    category_id = params.get('categoryId')
    description = params.get('description')
    title = params.get('title')
    asset = Asset.find_by_id(asset_id) if asset_id else None
    if not asset or not title:
        raise BadRequestError('Asset update requires a valid ID and title.')
    if not can_update_asset(asset=asset, user=current_user):
        raise BadRequestError('To update an asset you must own it or be a teacher in the course.')
    asset = Asset.update(
        asset_id=asset_id,
        categories=category_id and [Category.find_by_id(category_id)],
        description=description,
        title=title,
    )
    return tolerant_jsonify(asset.to_api_json(user_id=current_user.get_id()))


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def _load_json(path):
    try:
        file = open(f"{app.config['BASE_DIR']}/{path}")
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


def _get_asset_for_like(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if not asset or not can_view_asset(asset=asset, user=current_user):
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')
    elif current_user.user in asset.users:
        raise BadRequestError('You cannot like your own asset.')
    else:
        return asset


def _get_upload_from_http_post():
    request_files = request.files
    file = request_files.get('file[0]')
    if not file:
        raise BadRequestError('request.files is empty')

    filename = file.filename and file.filename.strip()
    if not filename:
        raise BadRequestError(f'Invalid file: {filename}')

    return {
        'name': filename.rsplit('/', 1)[-1],
        'byte_stream': file.read(),
    }
