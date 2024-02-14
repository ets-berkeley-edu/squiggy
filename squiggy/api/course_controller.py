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

from flask import current_app as app, request
from flask_login import current_user, login_required
from squiggy.api.api_util import teacher_required
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.course import Course


@app.route('/api/course/activate', methods=['POST'])
@teacher_required
def activate():
    course = Course.find_by_id(current_user.course_id)
    course.activate()
    return tolerant_jsonify(True)


@app.route('/api/course/is_active')
@login_required
def is_active():
    return tolerant_jsonify(Course.is_active(current_user.course_id))


@app.route('/api/course/<course_id>/advanced_asset_search_options')
@login_required
def get_advanced_asset_search_options(course_id):
    search_options = Course.get_advanced_asset_search_options(
        course_id,
        current_user_sections=current_user.canvas_course_sections,
        is_current_user_student=current_user.is_student,
    )
    return tolerant_jsonify(search_options)


@app.route('/api/course/<course_id>')
@login_required
def get_course(course_id):
    return tolerant_jsonify(Course.find_by_id(course_id).to_api_json())


@app.route('/api/course/update_protect_assets_per_section', methods=['POST'])
@teacher_required
def update_protect_assets_per_section_checkbox():
    params = request.get_json()
    protect_assets_per_section = params.get('protectSectionCheckbox')
    Course.update_protect_assets_per_section(current_user.course_id, protect_assets_per_section)
    return tolerant_jsonify({'status': 'success'})
