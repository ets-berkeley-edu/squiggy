"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from squiggy.api.api_util import can_current_user_delete_comment, can_current_user_update_comment, can_current_user_view_asset
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import Asset
from squiggy.models.comment import Comment
from squiggy.models.user import User


@app.route('/api/comment/create', methods=['POST'])
@login_required
def create_comment():
    params = request.get_json()
    asset_id = params.get('assetId')
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset and can_current_user_view_asset(asset=asset):
        body = params.get('body', '').strip()
        if not body:
            raise BadRequestError('Comment body is required.')
        parent_id = params.get('parentId')
        comment = Comment.create(
            asset=asset,
            user_id=current_user.user_id,
            body=body,
            parent_id=parent_id and int(parent_id),
        )
        return tolerant_jsonify(_decorate_comments([comment.to_api_json()])[0])
    else:
        raise ResourceNotFoundError('Asset is either unavailable or non-existent.')


@app.route('/api/comments/<asset_id>')
@login_required
def get_comments(asset_id):
    asset = Asset.find_by_id(asset_id=asset_id)
    if asset and can_current_user_view_asset(asset=asset):
        return tolerant_jsonify(_decorate_comments(Comment.get_comments(asset.id)))
    else:
        raise ResourceNotFoundError('Asset is either unavailable or non-existent.')


@app.route('/api/comment/<comment_id>/delete', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.find_by_id(comment_id=comment_id)
    if comment and can_current_user_delete_comment(comment=comment):
        Comment.delete(comment_id=comment_id)
        return tolerant_jsonify({'message': f'Comment {comment_id} deleted'}), 200
    else:
        raise ResourceNotFoundError('Comment is either unavailable or non-existent.')


@app.route('/api/comment/<comment_id>/update', methods=['POST'])
@login_required
def update_comment(comment_id):
    params = request.get_json()
    comment = Comment.find_by_id(comment_id=comment_id)
    if comment and can_current_user_update_comment(comment=comment):
        body = params.get('body', '').strip()
        if not body:
            raise BadRequestError('Comment body is required.')
        comment = Comment.update(body=body, comment_id=comment.id)
        return tolerant_jsonify(_decorate_comments([comment.to_api_json()])[0])
    else:
        raise ResourceNotFoundError('Asset is either unavailable or non-existent.')


def _decorate_comments(comments):
    user_ids = []
    for comment in comments:
        user_ids.append(comment['userId'])
        for reply in comment.get('replies', []):
            user_ids.append(reply['userId'])
    users_by_id = {user.id: user for user in User.find_by_ids(user_ids)}
    for comment in comments:
        comment['user'] = users_by_id[comment['userId']].to_api_json()
        for reply in comment.get('replies', []):
            reply['user'] = users_by_id[reply['userId']].to_api_json()
    return comments
