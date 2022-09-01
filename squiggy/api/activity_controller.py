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
from squiggy.api.api_util import activities_type_enums, teacher_required
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.lib.http import response_with_csv_download, tolerant_jsonify
from squiggy.models.activity import Activity
from squiggy.models.activity_type import ActivityType
from squiggy.models.user import User


@app.route('/api/activities/configuration', methods=['GET'])
@login_required
def get_activity_configuration():
    configuration = ActivityType.get_activity_type_configuration(course_id=current_user.course.id)
    return tolerant_jsonify(configuration)


@app.route('/api/activities/configuration', methods=['POST'])
@teacher_required
def update_activity_configuration():
    params = request.get_json()
    for update in params:
        if (
            type(update) is not dict
            or update.get('type', None) not in activities_type_enums()
            or 'points' not in update
            or 'enabled' not in update
        ):
            raise BadRequestError('Activity updates not properly formatted.')
    ActivityType.update_activity_type_configuration(
        course_id=current_user.course.id,
        updates=params,
    )
    Activity.recalculate_points(course_id=current_user.course.id)
    return tolerant_jsonify({'updated': True})


@app.route('/api/activities/csv', methods=['GET'])
@teacher_required
def get_activity_csv():
    course_id = current_user.course.id
    fieldnames, rows = Activity.get_activities_as_csv(course_id=course_id)
    filename_prefix = f'engagement_index_activities_{current_user.course.canvas_course_id}'
    return response_with_csv_download(rows, filename_prefix, fieldnames)


@app.route('/api/activities/interactions', methods=['GET'])
@login_required
def get_interactions():
    interactions = Activity.get_interactions_for_course(course_id=current_user.course.id)
    return tolerant_jsonify(interactions)


@app.route('/api/activities/user/<user_id>', methods=['GET'])
@login_required
def get_user_activities(user_id):
    user = User.find_by_id(user_id)
    if not user or user.course.id != current_user.course.id:
        raise ResourceNotFoundError('User not found.')
    activities_feed = Activity.get_activities_for_user_id(user_id)
    return tolerant_jsonify(activities_feed)
