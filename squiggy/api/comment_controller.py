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

from flask import current_app as app, request
from flask_login import current_user, login_required
from squiggy.api.api_util import can_view_asset
from squiggy.api.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import Asset
from squiggy.models.comment import Comment


@app.route('/api/comment/create', methods=['POST'])
@login_required
def create_comment():
    params = request.get_json()
    asset_id = params.get('assetId')
    body = params.get('body', '').strip()
    parent_id = params.get('parentId')
    if not asset_id or not body:
        raise BadRequestError('Comment creation requires assetId and body.')
    comment = Comment.create(
        asset_id=asset_id and int(asset_id),
        user_id=current_user.user_id,
        body=body,
        parent_id=parent_id and int(parent_id),
    )
    return tolerant_jsonify(comment.to_api_json())


@app.route('/api/comments/<asset_id>')
@login_required
def get_comments(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset and can_view_asset(asset=asset, user=current_user):
        return tolerant_jsonify(Comment.get_comments(asset.id))
    else:
        raise ResourceNotFoundError(f'No comment found with id: {asset_id}')
