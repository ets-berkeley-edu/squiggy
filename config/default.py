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

import logging
import os

API_PREFIX = 'https://example.com/api'

AWS_ACCESS_KEY_ID = 'some id'
AWS_SECRET_ACCESS_KEY = 'some secret'
AWS_S3_BUCKET_FOR_ASSETS = None
AWS_S3_REGION = 'us-west-2'

# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

BOOKMARKLET_ENCRYPTION_KEY = b'32 url-safe base64-encoded bytes'

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'
CAS_LOGOUT_URL = 'https://auth-test.berkeley.edu/cas/logout'

CANVAS_POLLER = True
CANVAS_POLLER_ACCEPTABLE_HOURS_SINCE_LAST = 1
CANVAS_POLLER_DEACTIVATION_THRESHOLD = 90

# Some defaults.
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'

DEVELOPER_AUTH_ENABLED = False
DEVELOPER_AUTH_PASSWORD = 'shotz_brewery'

DIST_STATIC_DIR = 'dist/static'

EMAIL_ADDRESS_SUPPORT = 'bcourseshelp@berkeley.edu'

FEATURE_FLAG_WHITEBOARDS = False

# Directory to search for mock fixtures, if running in "test" or "demo" mode.
FIXTURES_PATH = None

INACTIVE_SESSION_LIFETIME = 20

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'squiggy.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_PROPAGATION_LEVEL = logging.INFO

NODE_EXECUTABLE = '/usr/bin/node'

PREVIEWS_API_KEY = 'someKey'
# Assign PREVIEWS_CALLBACK_API_PREFIX to override API_PREFIX in context of preview-service callbacks. E.g., if you are
# running locally (unreachable by preview-service) then use PREVIEWS_CALLBACK_API_PREFIX to point at squiggy-dev.
# If PREVIEWS_CALLBACK_API_PREFIX is nil then Squiggy uses API_PREFIX config value.
PREVIEWS_CALLBACK_API_PREFIX = None
PREVIEWS_ENABLED = True
PREVIEWS_URL = 'https://example.com/previews'

# Where file assets go.
S3_BUCKET = 'some-bucket'
S3_REGION = 'us-west-2'

# Used to encrypt session cookie.
SECRET_KEY = 'secret'

# Required for session cookie to work inside iframes on Chrome.
SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

# Flask-SocketIO debug logging is verbose.
SOCKET_IO_DEBUG_MODE = False

# Save DB changes at the end of a request.
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# Override in local configs.
SQLALCHEMY_DATABASE_URI = 'postgresql://squiggy:squiggy@localhost:5432/squiggy'
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = None
SQLALCHEMY_POOL_TIMEOUT = None
SQLALCHEMY_RECORD_QUERIES = None

# Disable an expensive bit of the ORM.
SQLALCHEMY_TRACK_MODIFICATIONS = False

STATIC_PATH = '/static'

# A common configuration; one request thread, one background worker thread.
THREADS_PER_PAGE = 2

TIMEZONE = 'America/Los_Angeles'

# This base-URL config should only be non-None in the "local" env where the Vue front-end runs on port 8080.
VUE_LOCALHOST_BASE_URL = None

WHITEBOARD_SESSION_EXPIRATION_MINUTES = 2
# The following value is in milliseconds.
WHITEBOARDS_REFRESH_INTERVAL = 15000

# We keep these out of alphabetical sort above for readability's sake.
HOST = '0.0.0.0'
PORT = 5000
