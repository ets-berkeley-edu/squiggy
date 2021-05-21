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
from squiggy.api.api_util import teacher_required
from squiggy.lib.errors import BadRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import to_bool_or_none
from squiggy.models.category import Category


@app.route('/api/categories')
@login_required
def get_categories():
    include_hidden = to_bool_or_none(request.args.get('includeHidden'))
    categories = Category.get_categories_by_course_id(
        course_id=current_user.course.id,
        include_hidden=include_hidden,
    )
    return tolerant_jsonify(Category.to_decorated_json(categories))


@app.route('/api/category/create', methods=['POST'])
@teacher_required
def create_category():
    params = request.get_json() or request.form
    title = params.get('title')
    if not title:
        raise BadRequestError('Category creation requires title.')
    category = Category.create(
        canvas_assignment_name=title,
        course_id=current_user.course.id,
        title=title,
    )
    return tolerant_jsonify(category.to_api_json())


@app.route('/api/category/<category_id>/delete', methods=['DELETE'])
@teacher_required
def delete(category_id):
    Category.delete(category_id)
    return tolerant_jsonify({'message': f'Category {category_id} deleted'}), 200


@app.route('/api/category/update', methods=['POST'])
@teacher_required
def update_category():
    params = request.get_json()
    category_id = params.get('categoryId')
    title = params.get('title')
    visible = to_bool_or_none(params.get('visible'))
    category = Category.find_by_id(category_id) if category_id else None
    if not category or not title:
        raise BadRequestError('Category update requires categoryId and title.')
    category = Category.update(
        category_id=category_id,
        title=title,
        visible=category.visible if visible is None else visible,
    )
    return tolerant_jsonify(category.to_api_json())
