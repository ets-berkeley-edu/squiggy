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
from squiggy.models.activity import Activity
from squiggy.models.activity_type import ActivityType
from squiggy.models.asset import Asset
from squiggy.models.authorized_user import AuthorizedUser
from squiggy.models.canvas import Canvas
from squiggy.models.category import Category
from squiggy.models.comment import Comment
from squiggy.models.course import Course
from squiggy.models.user import User


_test_activities = [
    {
        'type': 'asset_add',
        'object_type': 'asset',
    },
    {
        'type': 'asset_comment',
        'object_type': 'comment',
    },
]

_test_activity_types = [
    {
        'type': 'asset_add',
        'points': 5,
        'enabled': True,
    },
    {
        'type': 'asset_comment',
        'points': 2,
        'enabled': True,
    },
]

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

_test_comments = [
    {
        'body': 'But mostly you just make me mad, baby, you just make me mad',
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
    users = _create_users(courses)
    assets = _create_assets(courses, users)
    _create_comments(assets, users)
    _create_activities(assets, users)
    _create_activity_types(courses)
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


def _create_users(courses):
    for test_authorized_user in _test_authorized_users:
        db.session.add(AuthorizedUser(uid=test_authorized_user['uid']))
    course = courses[0]
    users = []
    for test_user in _test_users:
        user = User.create(
            course_id=course.id,
            canvas_user_id=test_user['canvas_user_id'],
            canvas_course_role=test_user['canvas_course_role'],
            canvas_enrollment_state=test_user['canvas_enrollment_state'],
            canvas_full_name=test_user['canvas_full_name'],
            canvas_email=test_user['canvas_email'],
            canvas_course_sections=[],
        )
        users.append(user)
    std_commit(allow_test_environment=True)
    return users


def _create_assets(courses, users):
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

    user = users[0]

    assets = []
    for a in _test_assets:
        asset = Asset.create(
            asset_type=a['asset_type'],
            categories=[category],
            course_id=course_id,
            description=None,
            title=a['title'],
            url=a['url'],
            users=[user],
        )
        db.session.add(asset)
        assets.append(asset)
    std_commit(allow_test_environment=True)
    return assets


def _create_comments(assets, users):
    asset = assets[0]
    user = users[0]
    for test_comment in _test_comments:
        Comment.create(
            asset_id=asset.id,
            user_id=user.id,
            body=test_comment['body'],
        )
    std_commit(allow_test_environment=True)


def _create_activities(assets, users):
    asset = assets[0]
    user = users[0]
    for test_activity in _test_activities:
        Activity.create(
            activity_type=test_activity['type'],
            course_id=asset.course_id,
            user_id=user.id,
            object_type=test_activity['object_type'],
            object_id=asset.id,
            asset_id=asset.id,
        )
    std_commit(allow_test_environment=True)


def _create_activity_types(courses):
    course = courses[0]
    for test_activity_type in _test_activity_types:
        ActivityType.create(
            course_id=course.id,
            activity_type=test_activity_type['type'],
            enabled=test_activity_type['enabled'],
            points=test_activity_type['points'],
        )
    std_commit(allow_test_environment=True)


if __name__ == '__main__':
    import squiggy.factory
    squiggy.factory.create_app()
    load()
