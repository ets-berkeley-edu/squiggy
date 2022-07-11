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

import json

from flask import current_app as app, request
from squiggy import __version__ as version
from squiggy.api.api_util import assets_type_enums
from squiggy.lib.aws import S3_PREVIEW_URL_PATTERN
from squiggy.lib.http import tolerant_jsonify
from squiggy.models.asset import assets_sort_by_options


@app.route('/api/config')
def app_config():
    return tolerant_jsonify({
        'app': _app_version(),
        'assetTypes': assets_type_enums(),
        'baseUrl': app.config['VUE_LOCALHOST_BASE_URL'] or request.url_root,
        'ebEnvironment': app.config['EB_ENVIRONMENT'] if 'EB_ENVIRONMENT' in app.config else None,
        'emailAddressSupport': app.config['EMAIL_ADDRESS_SUPPORT'],
        'developerAuthEnabled': app.config['DEVELOPER_AUTH_ENABLED'],
        'featureFlagWhiteboards': app.config['FEATURE_FLAG_WHITEBOARDS'],
        'orderByOptions': assets_sort_by_options,
        's3PreviewUrlPattern': S3_PREVIEW_URL_PATTERN,
        'socketIoDebugMode': app.config['SOCKET_IO_DEBUG_MODE'],
        'squiggyEnv': app.config['SQUIGGY_ENV'],
        'staticPath': app.config['STATIC_PATH'],
        'timezone': app.config['TIMEZONE'],
        'whiteboardsRefreshInterval': app.config['WHITEBOARDS_REFRESH_INTERVAL'],
    })


@app.route('/api/version')
def app_version():
    return tolerant_jsonify(_app_version())


def load_json(relative_path):
    try:
        file = open(app.config['BASE_DIR'] + '/' + relative_path)
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None


def _app_version():
    summary = load_json('config/build-summary.json')
    return {
        'build': summary.get('build') if summary else None,
        'version': version,
    }
