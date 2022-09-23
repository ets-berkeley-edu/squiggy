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
from squiggy.lib.errors import BadRequestError, ForbiddenRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.user import User


@app.route('/api/profile/my')
def my_profile():
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/users')
@login_required
def get_users():
    sections = current_user.user.canvas_course_sections if current_user.is_student and current_user.course.protects_assets_per_section else None
    return tolerant_jsonify([u.to_api_json() for u in User.get_users_by_course_id(course_id=current_user.course.id, sections=sections)])


@app.route('/api/users/leaderboard')
@login_required
def get_leaderboard():
    if (current_user.is_admin or current_user.is_teaching):
        users = User.get_leaderboard(course_id=current_user.course.id, sharing_only=False)
        return tolerant_jsonify([u.to_api_json(include_points=True, include_sharing=True) for u in users])
    elif current_user.user.share_points:
        users = User.get_leaderboard(course_id=current_user.course.id, sharing_only=True)
        return tolerant_jsonify([u.to_api_json(include_points=True) for u in users])
    else:
        raise ForbiddenRequestError('Leaderboard disallowed for users not sharing points.')


@app.route('/api/users/me/looking_for_collaborators', methods=['POST'])
@login_required
def update_looking_for_collaborators():
    params = request.get_json()
    if 'lookingForCollaborators' not in params:
        raise BadRequestError('No looking for collaborators status provided.')
    current_user.user.update_looking_for_collaborators(params['lookingForCollaborators'])
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/users/me/personal_description', methods=['POST'])
@login_required
def update_personal_description():
    params = request.get_json()
    if 'personalDescription' not in params:
        raise BadRequestError('No personal description provided.')
    current_user.user.update_personal_description(params['personalDescription'])
    return tolerant_jsonify(current_user.to_api_json())


@app.route('/api/users/me/share', methods=['POST'])
@login_required
def update_share_points():
    params = request.get_json()
    if 'share' not in params:
        raise BadRequestError('No share status provided.')
    current_user.user.update_share_points(params['share'])
    return tolerant_jsonify(current_user.to_api_json())
