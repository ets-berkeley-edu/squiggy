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

from datetime import datetime
import json
import os
from random import randint, randrange

from moto import mock_sts  # noqa
import pytest  # noqa
from squiggy import std_commit
from squiggy.lib.login_session import LoginSession
from squiggy.models.asset import Asset
from squiggy.models.category import Category
from squiggy.models.comment import Comment
from squiggy.models.course import Course
from squiggy.models.user import User
import squiggy.factory  # noqa
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
    _app = squiggy.factory.create_app()

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
        db.session.get_bind().close()
    # The session bind will close only if it was provided a specific connection via this fixture.
    except AttributeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    options = dict(bind=connection, binds={})
    _session = db.create_scoped_session(options=options)
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
    return User.query.filter_by(canvas_course_role='Student').first().id


@pytest.fixture(scope='function')
def fake_auth(app, db, client):
    """Shortcut to start an authenticated session."""
    return FakeAuth(app, client)


@pytest.fixture(scope='session', autouse=True)
def fake_sts(app):
    """Fake the AWS security token service used to deliver S3 content (photos, note attachments)."""
    mock_sts().start()
    yield
    mock_sts().stop()


@pytest.fixture(scope='function')
def mock_asset(app, db_session):
    course = Course.create(
        canvas_api_domain='bcourses.berkeley.edu',
        canvas_course_id=randrange(1000000),
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
    course = Course.query.order_by(Course.name).all()[0]
    canvas_user_id = str(randint(1000000, 9999999))
    user = User.create(
        canvas_course_role='Student',
        canvas_course_sections=[],
        canvas_email=f'{canvas_user_id}@berkeley.edu',
        canvas_enrollment_state='active',
        canvas_full_name=f'Student {canvas_user_id}',
        canvas_user_id=canvas_user_id,
        course_id=course.id,
    )
    unique_token = datetime.now().isoformat()
    asset = Asset.create(
        asset_type='link',
        categories=[category_hidden, category_visible],
        course_id=course.id,
        description=None,
        download_url=f"s3://{app.config['AWS_S3_BUCKET_FOR_ASSETS']}/asset/{course.id}_{canvas_user_id}_{unique_token}.pdf",
        title=f'Mock Asset created at {unique_token}',
        url=f'https://en.wikipedia.org/wiki/{unique_token}',
        users=[user],
    )
    for test_comment in _get_mock_comments():
        comment = Comment.create(asset=asset, body=test_comment['body'], user_id=user.id)
        for reply in test_comment.get('replies', []):
            reply = Comment.create(
                asset=asset,
                body=reply['body'],
                parent_id=comment.id,
                user_id=user.id,
            )
    std_commit(allow_test_environment=True)
    yield asset
    db_session.delete(asset)
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
