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

from flask import current_app as app
from sqlalchemy.sql import text
from squiggy import db, std_commit
from squiggy.models.asset import Asset
from squiggy.models.authorized_user import AuthorizedUser
from squiggy.models.canvas import Canvas
from squiggy.models.category import Category
from squiggy.models.course import Course
from squiggy.models.user import User

_test_assets = [
    {
        'asset_type': 'link',
        'title': 'Pale Blue Eyes',
        'url': 'https://www.youtube.com/watch?v=KisHhIRihMY',
    },
    {
        'asset_type': 'link',
        'title': 'Who Loves The Sun',
        'url': 'https://www.youtube.com/watch?v=gNPovDOk4jY',
    },
]

_test_courses = [
    {
        'active': True,
        'canvas_api_domain': 'bcourses.berkeley.edu',
        'canvas_course_id': 123456,
    },
]

_test_canvas = [
    {
        'canvas_api_domain': 'bcourses.berkeley.edu',
        'api_key': 'qwerty',
        'lti_key': 'GrxUBuBcFYqUKFKqNkixiYUPJGonbedl',
        'lti_secret': 'zY8aw28nHZHbKkYjZP1XAXgfok0tj6aw',
        'name': 'bCourses',
    },
]

_test_authorized_users = [
    {
        'uid': '2040',
    },
]

_test_users = [
    {
        'canvas_user_id': '9876543',
        'canvas_course_role': 'Teacher',
        'canvas_enrollment_state': 'active',
        'canvas_full_name': 'Oliver Heyer',
        'canvas_email': 'oheyer@berkeley.edu',
    },
]


def clear():
    with open(app.config['BASE_DIR'] + '/scripts/db/drop_schema.sql', 'r') as ddlfile:
        db.session().execute(text(ddlfile.read()))
        std_commit()


def load():
    _load_schemas()
    courses = _create_courses()
    _create_assets(courses)
    _create_users()
    return db


def _load_schemas():
    """Create DB schema from SQL file."""
    with open(app.config['BASE_DIR'] + '/scripts/db/schema.sql', 'r') as ddlfile:
        db.session().execute(text(ddlfile.read()))
        std_commit()


def _create_courses():
    for c in _test_canvas:
        canvas = Canvas(
            canvas_api_domain=c['canvas_api_domain'],
            api_key=c['api_key'],
            lti_key=c['lti_key'],
            lti_secret=c['lti_secret'],
            name=c['name'],
        )
        db.session.add(canvas)
    std_commit(allow_test_environment=True)

    courses = []
    for c in _test_courses:
        course = Course(
            active=c['active'],
            canvas_api_domain=c['canvas_api_domain'],
            canvas_course_id=c['canvas_course_id'],
        )
        db.session.add(course)
        courses.append(course)
    std_commit(allow_test_environment=True)
    return courses


def _create_assets(courses):
    course_id = courses[0].id
    category = Category(
        canvas_assignment_name='Linger on your pale blue eyes',
        course_id=course_id,
        title='Thought of you as my mountain top',
        canvas_assignment_id=98765,
        visible=True,
    )
    db.session.add(category)
    std_commit(allow_test_environment=True)

    for a in _test_assets:
        Asset.create(
            asset_type=a['asset_type'],
            course_id=course_id,
            categories=[category],
            description=None,
            title=a['title'],
            url=a['url'],
        )
        # db.session.add(asset)
    std_commit(allow_test_environment=True)


def _create_users():
    for test_authorized_user in _test_authorized_users:
        db.session.add(AuthorizedUser(uid=test_authorized_user['uid']))
    course = Course.query.first()
    for test_user in _test_users:
        db.session.add(
            User(
                course_id=course.id,
                canvas_user_id=test_user['canvas_user_id'],
                canvas_course_role=test_user['canvas_course_role'],
                canvas_enrollment_state=test_user['canvas_enrollment_state'],
                canvas_full_name=test_user['canvas_full_name'],
                canvas_email=test_user['canvas_email'],
                canvas_course_sections=[],
            ),
        )
    std_commit(allow_test_environment=True)


if __name__ == '__main__':
    import squiggy.factory
    squiggy.factory.create_app()
    load()
