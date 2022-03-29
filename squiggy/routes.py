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

import datetime

from cryptography.fernet import Fernet, InvalidToken
from flask import jsonify, make_response, redirect, request, session
from flask_login import current_user, LoginManager
from flask_socketio import emit
from squiggy.api.api_util import start_login_session
from squiggy.lib.login_session import LoginSession
from squiggy.lib.util import is_admin, to_int
from squiggy.models.user import User


def register_routes(app, socketio):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(_user_loader)
    login_manager.anonymous_user = _user_loader

    # Register API routes.
    import squiggy.api.activity_controller
    import squiggy.api.asset_controller
    import squiggy.api.auth_controller
    import squiggy.api.canvas_controller
    import squiggy.api.category_controller
    import squiggy.api.comment_controller
    import squiggy.api.config_controller
    import squiggy.api.course_controller
    import squiggy.api.previews_controller
    import squiggy.api.status_controller
    import squiggy.api.user_controller
    import squiggy.api.whiteboard_controller
    import squiggy.api.whiteboard_element_controller

    # Register error handlers.
    import squiggy.api.error_handlers

    index_html = open(f"{app.config['DIST_STATIC_DIR']}/index.html").read()

    @app.login_manager.unauthorized_handler
    def unauthorized_handler():
        return jsonify(success=False, data={'login_required': True}, message='Unauthorized'), 401

    # Unmatched API routes return a 404.
    @app.route('/api/<path:path>')
    def handle_unmatched_api_route(**kwargs):
        app.logger.error('The requested resource could not be found.')
        raise squiggy.lib.errors.ResourceNotFoundError('The requested resource could not be found.')

    # Non-API routes are handled by the front end.
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def front_end_route(**kwargs):
        vue_base_url = app.config['VUE_LOCALHOST_BASE_URL']
        return redirect(vue_base_url + request.full_path) if vue_base_url else make_response(index_html)

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=app.config['INACTIVE_SESSION_LIFETIME'])
        session.modified = True

    @app.after_request
    def after_request(response):
        if app.config['SQUIGGY_ENV'] == 'development':
            # In development the response can be shared with requesting code from any local origin.
            allowed_headers = 'Content-Type,Squiggy-Bookmarklet-Auth,Squiggy-Canvas-Api-Domain,Squiggy-Canvas-Course-Id'
            response.headers['Access-Control-Allow-Headers'] = allowed_headers
            response.headers['Access-Control-Allow-Origin'] = app.config['VUE_LOCALHOST_BASE_URL']
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'

        if request.full_path.startswith('/api'):
            log_message = ' '.join([
                request.remote_addr,
                request.method,
                request.full_path,
                response.status,
            ])
            if response.status_code >= 500:
                app.logger.error(log_message)
            elif response.status_code >= 400:
                app.logger.warning(log_message)
            else:
                app.logger.debug(log_message)

        return response

    @socketio.on('connect')
    def connect_handler():
        _handle_socketio_connect()

    @socketio.on('add_whiteboard_elements')
    def add_whiteboard_elements(data):
        from squiggy.api.api_whiteboard_util import create_whiteboard_elements

        create_whiteboard_elements(
            user=LoginSession(data.get('userId')),
            whiteboard_id=data.get('whiteboardId'),
            whiteboard_elements=data.get('whiteboardElements', []),
        )


def _handle_socketio_connect():
    if current_user.is_authenticated:
        emit('my response', {'message': '{0} has joined'.format(current_user.name)}, broadcast=True)
    else:
        return False  # not allowed here


def _user_loader(user_id=None):
    from squiggy.lib.login_session import LoginSession
    from flask import current_app as app

    user_session = LoginSession(user_id)
    bookmarklet_auth = request.headers.get('Squiggy-Bookmarklet-Auth')
    canvas_api_domain = request.headers.get('Squiggy-Canvas-Api-Domain')
    canvas_course_id = request.headers.get('Squiggy-Canvas-Course-Id')

    if bookmarklet_auth:
        user_session.logout()
        encryption_key = app.config['BOOKMARKLET_ENCRYPTION_KEY']
        try:
            args = Fernet(encryption_key).decrypt(bytes(bookmarklet_auth, 'utf-8')).decode().rsplit('_')
            if len(args) == 3:
                user_id = to_int(args[0])
                course_id = to_int(args[1])
                bookmarklet_token = args[2]
                user = user_id and User.find_by_id(user_id)

                if _is_authorized_bookmarklet(bookmarklet_token=bookmarklet_token, course_id=course_id, user=user):
                    user_session = LoginSession(user_id)
                    start_login_session(user_session)
        except InvalidToken as e:
            app.logger.error('Failed to authenticate per Squiggy-Bookmarklet-Auth header')
            app.logger.exception(e)
    elif user_session.is_authenticated and canvas_api_domain and canvas_course_id:
        # Check for conflicts between existing login session and course headers.
        course = user_session.course
        if canvas_api_domain != course.canvas_api_domain or str(canvas_course_id) != str(course.canvas_course_id):
            app.logger.info(
                f'Session data (canvas_api_domain={course.canvas_api_domain}, canvas_course_id={course.canvas_course_id}) '
                f'conflicts with headers (canvas_api_domain={canvas_api_domain}, canvas_course_id={canvas_course_id}, logging out user')
            user_session.logout()

    if not user_session.is_authenticated:
        app.logger.info(f'_user_loader: canvas_api_domain={canvas_api_domain}, canvas_course_id={canvas_course_id}')
        if canvas_api_domain and canvas_course_id:
            cookie_value = request.cookies.get(f'{canvas_api_domain}|{canvas_course_id}')
            user_id = cookie_value and to_int(cookie_value)
            if user_id:
                candidate = LoginSession(user_id)
                course = candidate.course
                if course.canvas_api_domain == canvas_api_domain and str(course.canvas_course_id) == str(canvas_course_id):
                    # User must be a member of the Canvas course site.
                    user_session = candidate
                    app.logger.info(f'User {user_id} loaded.')
                    start_login_session(user_session)
    return user_session


def _is_authorized_bookmarklet(bookmarklet_token, course_id, user):
    if not user or user.bookmarklet_token != bookmarklet_token:
        return False
    else:
        return is_admin(user) or (user.course_id == course_id and user.canvas_enrollment_state in ['active', 'invited'])
