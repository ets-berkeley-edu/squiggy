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

from datetime import datetime
import json
import os
from random import randint
from uuid import uuid4

from flask_login import logout_user
from moto import mock_sts  # noqa
import pytest  # noqa
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from squiggy import std_commit
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import is_student
from squiggy.models.asset import Asset
from squiggy.models.category import Category
from squiggy.models.comment import Comment
from squiggy.models.course import Course
from squiggy.models.course_group import CourseGroup
from squiggy.models.course_group_membership import CourseGroupMembership
from squiggy.models.user import User
import squiggy.factory  # noqa
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from tests.util import override_config  # noqa

os.environ['SQUIGGY_ENV'] = 'test'  # noqa


class FakeAuth(object):
    def __init__(self, the_app, the_client):
        self.app = the_app
        self.client = the_client

    def login(
            self,
            user_id,
    ):
        with override_config(self.app, 'DEVELOPER_AUTH_ENABLED', True):
            params = {
                'userId': user_id,
                'password': self.app.config['DEVELOPER_AUTH_PASSWORD'],
            }
            self.client.post(
                '/api/auth/dev_auth_login',
                data=json.dumps(params),
                content_type='application/json',
            )


# Because app and db fixtures are only created once per pytest run, individual tests
# are not able to modify application configuration values before the app is created.
# Per-test customizations could be supported via a fixture scope of 'function' and
# the @pytest.mark.parametrize annotation.

@pytest.fixture(scope='session')
def app(request):
    """Fixture application object, shared by all tests."""
    _app, socketio = squiggy.factory.create_app()

    # Create app context before running tests.
    ctx = _app.app_context()
    ctx.push()

    # Pop the context after running tests.
    def teardown():
        ctx.pop()
    request.addfinalizer(teardown)

    return _app


# TODO Perform DB schema creation and deletion outside an app context, enabling test-specific app configurations.
@pytest.fixture(scope='session')
def db(app):
    """Fixture database object, shared by all tests."""
    from squiggy.models import development_db
    # Drop all tables before re-loading the schemas.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    _db = development_db.load()

    return _db


@pytest.fixture(scope='function', autouse=True)
def db_session(db):
    """Fixture database session used for the scope of a single test.

    All executions are wrapped in a session and then rolled back to keep individual tests isolated.
    """
    # Mixing SQL-using test fixtures with SQL-using decorators seems to cause timing issues with pytest's
    # fixture finalizers. Instead of using a finalizer to roll back the session and close connections,
    # we begin by cleaning up any previous invocations.
    # This fixture is marked 'autouse' to ensure that cleanup happens at the start of every test, whether
    # or not it has an explicit database dependency.
    db.session.rollback()
    try:
        bind = db.session.get_bind()
        if isinstance(bind, Engine):
            bind.dispose()
        else:
            bind.close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except TypeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    _session = scoped_session(sessionmaker(bind=connection))
    db.session = _session

    return _session


@pytest.fixture(scope='function')
def authorized_user_id():
    return 1


@pytest.fixture(scope='function')
def authorized_user_session(authorized_user_id):
    return LoginSession(authorized_user_id)


@pytest.fixture(scope='function')
def student_id():
    return _get_student().id


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    yield FakeAuth(app, client)
    logout_user()


@pytest.fixture(scope='session', autouse=True)
def fake_sts(app):
    """Fake the AWS security token service used to deliver S3 content (photos, note attachments)."""
    mock_sts().start()
    yield
    mock_sts().stop()


@pytest.fixture(scope='function')
def mock_asset(app, db_session):
    course = Course.find_by_canvas_course_id(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=1502870,
    )
    category_hidden = Category.create(
        canvas_assignment_name='Just look into her false colored eyes',
        course_id=course.id,
        title='What a clown (visible=False)',
        canvas_assignment_id=98765,
        visible=False,
    )
    category_visible = Category.create(
        canvas_assignment_name='Just look into her false colored eyes',
        course_id=course.id,
        title='What a clown (visible=True)',
        canvas_assignment_id=98765,
        visible=True,
    )
    user_1 = _create_student(course.id, canvas_course_sections=['section A'])
    user_2 = _create_student(course.id, canvas_course_sections=['section B'])
    asset1 = _create_asset(
        app=app,
        categories=[category_hidden, category_visible],
        course=course,
        users=[user_1],
    )
    asset2 = _create_asset(
        app=app,
        categories=[category_hidden, category_visible],
        course=course,
        users=[user_2],
    )
    for test_comment in _get_mock_comments():
        comment = Comment.create(asset=asset1, body=test_comment['body'], user_id=user_2.id)
        for reply in test_comment.get('replies', []):
            Comment.create(
                asset=asset1,
                body=reply['body'],
                parent_id=comment.id,
                user_id=user_1.id,
            )
    std_commit(allow_test_environment=True)
    yield asset1
    db_session.delete(asset1)
    db_session.delete(asset2)
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_asset_course(mock_asset):
    course = Course.find_by_id(mock_asset.course_id)
    yield course
    course.protects_assets_per_section = False
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_asset_users(mock_asset):
    asset_owner = User.find_by_id(mock_asset.created_by)
    course_users = Course.find_by_id(mock_asset.course_id).users
    same_section_student = next(user for user in course_users if _is_same_section_student(asset_owner, user))
    different_section_student = next(
        (user for user in course_users if _is_different_section_student(asset_owner, user) and user.id != same_section_student.id),
    )
    mock_asset.users = [mock_asset.users[0], same_section_student, different_section_student]
    std_commit(allow_test_environment=True)
    yield asset_owner, same_section_student, different_section_student
    mock_asset.users = [asset_owner]
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_course_group(app, db_session):
    course = Course.find_by_canvas_course_id(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=1502870,
    )
    group = CourseGroup.create(
        course_id=course.id,
        canvas_group_id=363901,
        name='Laverne & Shirley',
        category_name='Happy Days Televisual Universe (HDTU)',
    )
    user1 = _create_student(course.id)
    user2 = _create_student(course.id)
    membership1 = CourseGroupMembership.create(course_id=course.id, course_group_id=group.id, canvas_user_id=user1.canvas_user_id)
    membership2 = CourseGroupMembership.create(course_id=course.id, course_group_id=group.id, canvas_user_id=user2.canvas_user_id)
    other_group = CourseGroup.create(
        course_id=course.id,
        canvas_group_id=363901,
        name='Mork & Mindy',
        category_name='Happy Days Televisual Universe (HDTU)',
    )
    user3 = _create_student(course.id)
    membership3 = CourseGroupMembership.create(course_id=course.id, course_group_id=other_group.id, canvas_user_id=user3.canvas_user_id)
    std_commit(allow_test_environment=True)
    yield group
    db_session.delete(membership1)
    db_session.delete(membership2)
    db_session.delete(membership3)
    std_commit(allow_test_environment=True)
    db_session.delete(group)
    db_session.delete(other_group)
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_other_course_user(app, db_session):
    course = Course.find_by_canvas_course_id(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=1502871,
    )
    user = _create_student(course.id)
    std_commit(allow_test_environment=True)
    yield user
    db_session.delete(user)
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_whiteboard(app, db_session):
    course = Course.find_by_canvas_course_id(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=1502870,
    )
    users = []
    for section in ['section A', 'section B']:
        users.append(_create_student(course.id, canvas_course_sections=[section]))
    student_1 = users[0]
    whiteboard = Whiteboard.create(
        course_id=course.id,
        created_by=student_1.id,
        title=f'Mock Whiteboard of users {[u.canvas_user_id for u in users]}',
        users=users,
    )
    std_commit(allow_test_environment=True)
    asset = _create_asset(app=app, course=course, users=[student_1])
    whiteboard_id = whiteboard['id']
    for (z_index, element) in enumerate([
        {
            'assetId': asset.id,
            'height': 600,
            'type': 'asset',
            'uuid': str(uuid4()),
            'width': 800,
        },
        {
            'fill': 'rgb(0,0,0)',
            'fontSize': 14,
            'text': 'I am text.',
            'type': 'text',
            'uuid': str(uuid4()),
        },
        {
            'fill': 'rgb(0,0,0)',
            'fontSize': 14,
            'text': 'What are words for?',
            'type': 'text',
            'uuid': str(uuid4()),
        },
    ]):
        WhiteboardElement.create(
            asset_id=element.get('assetId'),
            element=element,
            uuid=element['uuid'],
            whiteboard_id=whiteboard_id,
            z_index=z_index,
        )
        std_commit(allow_test_environment=True)

    yield Whiteboard.find_by_id(
        current_user=LoginSession(student_1.id),
        whiteboard_id=whiteboard_id,
    )

    Whiteboard.delete(whiteboard_id=whiteboard_id)
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_whiteboard_course(mock_whiteboard):
    course = Course.find_by_id(mock_whiteboard['courseId'])
    yield course
    course.protects_assets_per_section = False
    std_commit(allow_test_environment=True)


@pytest.fixture(scope='function')
def mock_category(db):
    return Category.create(
        canvas_assignment_name='Linger on your pale blue eyes',
        course_id=1,
        title='Thought of you as my mountain top',
        canvas_assignment_id=98765,
        visible=True,
    )


def _create_asset(app, course, users, categories=None):
    unique_token = datetime.now().isoformat()
    return Asset.create(
        asset_type='link',
        categories=categories,
        course_id=course.id,
        created_by=users[0].id,
        description=None,
        download_url=f"s3://{app.config['AWS_S3_BUCKET_FOR_ASSETS']}/asset/{course.id}_{unique_token}.pdf",
        title=f'Mock Asset created at {unique_token}',
        url=f'https://en.wikipedia.org/wiki/{unique_token}',
        users=users,
    )


def _create_student(course_id, canvas_course_sections=None):
    canvas_user_id = str(randint(1000000, 9999999))
    return User.create(
        canvas_course_role='Student',
        canvas_course_sections=canvas_course_sections or [],
        canvas_email=f'{canvas_user_id}@berkeley.edu',
        canvas_enrollment_state='active',
        canvas_full_name=f'Student {canvas_user_id}',
        canvas_user_id=canvas_user_id,
        course_id=course_id,
    )


def _get_mock_comments():
    return [
        {
            'body': 'But mostly you just make me mad, baby, you just make me mad',
            'replies': [
                {
                    'body': 'In what costume shall the poor girl wear to all tomorrow\'s parties?',
                },
                {
                    'body': 'For Thursday\'s child is Sunday\'s clown, for whom none will go mourning.',
                },
            ],
        },
        {
            'body': 'And where will she go, and what shall she do, when midnight comes around?',
        },
    ]


def _get_student():
    return User.query.filter_by(canvas_course_role='Student', canvas_enrollment_state='active').first()


def _is_different_section_student(asset_owner, user):
    return user.id != asset_owner.id and is_student(user) and len(
        list(set(user.canvas_course_sections) & set(asset_owner.canvas_course_sections)),
    ) == 0


def _is_same_section_student(asset_owner, user):
    return user.id != asset_owner.id and is_student(user) and len(
        list(set(user.canvas_course_sections) & set(asset_owner.canvas_course_sections)),
    ) > 0
