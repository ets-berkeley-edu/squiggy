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

import os

from flask import Flask
from squiggy import db
from squiggy.configs import load_configs
from squiggy.lib.canvas_poller import launch_pollers
from squiggy.lib.socket_io_util import create_mock_socket, initialize_socket_io
from squiggy.lib.whiteboard_housekeeping import launch_whiteboard_housekeeping
from squiggy.logger import initialize_app_logger
from squiggy.routes import register_routes
from squiggy.sockets import register_sockets


def create_app():
    """Initialize app with configs."""
    app = Flask(__name__.split('.')[0])
    load_configs(app)
    initialize_app_logger(app)
    db.init_app(app)
    socketio = create_mock_socket() if app.config['TESTING'] else initialize_socket_io(app)

    with app.app_context():
        register_routes(app)
        register_sockets(socketio)

        # See https://stackoverflow.com/questions/9449101/how-to-stop-flask-from-initialising-twice-in-debug-mode
        if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            if app.config['CANVAS_POLLER']:
                launch_pollers()
            if app.config['FEATURE_FLAG_WHITEBOARDS']:
                launch_whiteboard_housekeeping()

    return app, socketio
