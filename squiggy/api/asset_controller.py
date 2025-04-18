"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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

from flask import current_app as app, request, Response
from flask_login import current_user, login_required
from squiggy.api.api_util import can_current_user_view_asset
from squiggy.lib.aws import stream_object
from squiggy.lib.errors import ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import local_now
from squiggy.models.asset import Asset


@app.route('/api/asset/<asset_id>/download')
@login_required
def download(asset_id):
    asset = Asset.find_by_id(asset_id)
    s3_url = asset.download_url
    if asset and s3_url and can_current_user_view_asset(asset=asset):
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
    if asset and can_current_user_view_asset(asset=asset):
        return tolerant_jsonify(asset.to_api_json(user_id=current_user.id))
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
        'group_id': _get(params, 'groupId', None),
        'keywords': _get(params, 'keywords', None),
        'owner_id': _get(params, 'userId', None),
        'section': _get(params, 'section', None),
    }
    results = Asset.get_assets(
        current_user=current_user,
        filters=filters,
        limit=limit,
        offset=offset,
        order_by=order_by,
    )
    return tolerant_jsonify(results)


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value
