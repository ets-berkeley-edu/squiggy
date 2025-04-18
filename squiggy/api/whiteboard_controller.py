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

from flask import current_app as app, request, send_file
from flask_login import current_user, login_required
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.file_remover import file_remover
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import local_now
from squiggy.lib.whiteboard_util import to_png_file
from squiggy.logger import logger
from squiggy.models.whiteboard import Whiteboard


@app.route('/api/whiteboard/<whiteboard_id>')
@login_required
def get_whiteboard(whiteboard_id):
    if Whiteboard.can_update_whiteboard(current_user=current_user, whiteboard_id=whiteboard_id):
        whiteboard = Whiteboard.find_by_id(current_user=current_user, whiteboard_id=whiteboard_id)
        return tolerant_jsonify(whiteboard)
    else:
        raise ResourceNotFoundError('Whiteboard not found')


@app.route('/api/whiteboard/<whiteboard_id>/download/png')
@login_required
def export_as_png(whiteboard_id):
    whiteboard = Whiteboard.find_by_id(
        current_user=current_user,
        whiteboard_id=whiteboard_id,
    )
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
        path_to_file = png_file.name
        response = send_file(
            as_attachment=True,
            download_name=f'{filename}_{now}.png',
            path_or_file=path_to_file,
        )
        file_remover.clean_up_when_done(response, path_to_file)
        logger.info(f'Delete transient file {path_to_file}')
        return response
    else:
        raise BadRequestError('Failed to generate whiteboard PNG')


@app.route('/api/whiteboards', methods=['POST'])
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
        course_id=current_user.course_id,
        current_user=current_user,
        include_deleted=include_deleted,
        keywords=keywords,
        limit=limit,
        offset=offset,
        order_by=order_by,
        user_id=user_id,
    )
    return tolerant_jsonify(summary)
