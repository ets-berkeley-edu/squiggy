"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from datetime import datetime
import json
import os
import re

from flask import current_app as app, request, Response
from flask_login import current_user, login_required
from squiggy.api.api_util import can_update_asset, can_view_asset
from squiggy.api.errors import BadRequestError, InternalServerError, ResourceNotFoundError
from squiggy.lib.aws import put_binary_data_to_s3, stream_object
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import Asset
from squiggy.models.category import Category
from squiggy.models.user import User


@app.route('/api/asset/<asset_id>/download')
@login_required
def download(asset_id):
    asset = Asset.find_by_id(asset_id)
    s3_url = asset.download_url
    if asset and s3_url and can_view_asset(current_user, asset):
        stream = stream_object(s3_url)
        if stream:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
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
        return tolerant_jsonify(asset.to_api_json())
    else:
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')


@app.route('/api/assets', methods=['POST'])
@login_required
def get_assets():
    params = request.get_json()
    sort = _get(params, 'sort', None)
    offset = params.get('offset')
    limit = params.get('limit')
    filters = {
        'asset_type': _get(params, 'assetType', None),
        'category_id': _get(params, 'categoryId', None),
        'has_comments': _get(params, 'hasComments', None),
        'has_likes': _get(params, 'hasLikes', None),
        'has_views': _get(params, 'hasViews', None),
        'keywords': _get(params, 'keywords', None),
        'order_by': _get(params, 'orderBy', 'recent'),
        'owner_id': _get(params, 'userId', None),
        'section_id': _get(params, 'sectionId', None),
    }
    results = Asset.get_assets(session=current_user, sort=sort, offset=offset, limit=limit, filters=filters)
    return tolerant_jsonify(results)


@app.route('/api/asset/create', methods=['POST'])
@login_required
def create_asset():
    params = request.get_json() or request.form
    asset_type = params.get('type')
    category_id = params.get('categoryId')
    description = params.get('description')
    source = params.get('source')
    url = params.get('url')
    title = params.get('title', url)
    visible = params.get('visible', True)
    if not asset_type or not title:
        raise BadRequestError('Asset creation requires title and type.')

    if asset_type == 'link' and not url:
        raise BadRequestError('Link asset creation requires url.')

    if not current_user.course:
        raise BadRequestError('Course data not found')

    content_type = None
    download_url = None
    if asset_type == 'file':
        file_upload = _get_upload_from_http_post()
        # S3 key begins with course id, reversed for performant key distribution, padded for readability.
        bucket = app.config['S3_BUCKET']
        reverse_course = str(current_user.course.id)[::-1].rjust(7, '0')
        (filename, extension) = os.path.splitext(file_upload['name'])
        # Truncate file basename if longer than 170 characters; the complete constructed S3 URI must come in under 255.
        key = f"{reverse_course}/assets/{datetime.now().strftime('%Y-%m-%d_%H%M%S')}-{filename[0:170]}{extension}"
        if put_binary_data_to_s3(bucket, key, file_upload['byte_stream']):
            download_url = f's3://{bucket}/{key}'
            # TODO determine content type for preview service
        else:
            raise InternalServerError('Could not upload file.')

    asset = Asset.create(
        asset_type=asset_type,
        categories=Category.get_categories_by_id([category_id]) if category_id else None,
        course_id=current_user.course.id,
        description=description,
        download_url=download_url,
        mime=content_type,
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
        raise BadRequestError('To delete this asset you must own it or be a teacher in the course.')
    Asset.delete(asset_id=asset_id)
    return tolerant_jsonify({'message': f'Asset {asset_id} deleted'}), 200


@app.route('/api/asset/<asset_id>/like')
@login_required
def like_asset(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset and can_view_asset(asset=asset, user=current_user):
        # TODO: Implement Asset.like and write pytests
        return tolerant_jsonify(asset.to_api_json())
    else:
        raise ResourceNotFoundError(f'No asset found with id: {asset_id}')


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
        categories=Category.get_categories_by_id([category_id]) if category_id else None,
        description=description,
        title=title,
    )
    return tolerant_jsonify(asset.to_api_json())


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def _load_json(path):
    try:
        file = open(f"{app.config['BASE_DIR']}/{path}")
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


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
