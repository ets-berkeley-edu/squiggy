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

from flask import current_app as app, request
from squiggy.lib.errors import BadRequestError, InternalServerError, UnauthorizedRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.previews import verify_preview_service_authorization
from squiggy.lib.util import utc_now
from squiggy.logger import logger
from squiggy.models.asset import Asset
from squiggy.models.whiteboard import Whiteboard


@app.route('/api/previews/callback', methods=['POST'])
def previews_callback():
    return _handle_previews_callback('asset')


@app.route('/api/previews/whiteboard/callback', methods=['POST'])
def whiteboard_previews_callback():
    return _handle_previews_callback('whiteboard')


def _handle_previews_callback(object_type):
    if not verify_preview_service_authorization(request.headers.get('authorization')):
        raise UnauthorizedRequestError('Missing or invalid authorization header.')

    params = request.form
    if not (params.get('id', None) and params.get('status', None)):
        raise BadRequestError('Id and status fields required.')
    metadata = None
    try:
        if params.get('metadata'):
            metadata = json.loads(params['metadata'])
        if params.get('status') == 'done':
            metadata = metadata or {}
            metadata['updatedAt'] = utc_now().isoformat()
    except Exception as e:
        logger.error('Failed to parse JSON preview metadata.')
        logger.exception(e)
        raise BadRequestError('Could not parse JSON metadata.')

    success = False
    if object_type == 'asset':
        success = _update_asset_preview(metadata=metadata, params=params)
    elif object_type == 'whiteboard':
        success = _update_whiteboard_preview(params=params)
    if success:
        return tolerant_jsonify({'status': 'success'})
    else:
        raise InternalServerError(f"Unable to update preview data ({object_type}_id={params['id']}.")


def _update_asset_preview(metadata, params):
    asset_id = params['id']
    asset = Asset.find_by_id(asset_id)
    if not asset:
        raise BadRequestError(f'Asset {asset_id} not found.')

    return asset.update_preview(
        preview_status=params.get('status'),
        thumbnail_url=params.get('thumbnail'),
        image_url=params.get('image'),
        pdf_url=params.get('pdf'),
        metadata=metadata,
    )


def _update_whiteboard_preview(params):
    whiteboard_id = params['id']
    whiteboard = Whiteboard.find_by_id(whiteboard_id)
    if not whiteboard:
        raise BadRequestError(f'Whiteboard {whiteboard_id} not found.')

    return Whiteboard.update_preview(
        image_url=params.get('image'),
        thumbnail_url=params.get('thumbnail'),
        whiteboard_id=whiteboard_id,
    )
