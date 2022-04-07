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

import base64
import hashlib
import hmac

from flask import current_app as app
from squiggy.lib import http
from squiggy.lib.util import to_int, utc_now
from squiggy.logger import logger


def generate_previews(asset_id, asset_url):
    if not app.config['PREVIEWS_ENABLED']:
        return
    response = http.request(
        app.config['PREVIEWS_URL'],
        headers={'authorization': generate_preview_service_signature()},
        method='post',
        data={
            'id': asset_id,
            'url': asset_url,
            'postBackUrl': f"{app.config['API_PREFIX']}/previews/callback",
        },
    )
    if not response:
        logger.error(f'Error generating previews (asset_id={asset_id}, asset_url={asset_url}.')
    return response


def generate_preview_service_signature(nonce=None):
    if not nonce:
        nonce = str(int(utc_now().timestamp() * 1000))
    digester = hmac.new(_byte_string(app.config['PREVIEWS_API_KEY']), _byte_string(nonce), hashlib.sha1)
    return f"Bearer {nonce}:{base64.b64encode(digester.digest()).decode('utf-8')}"


def verify_preview_service_authorization(auth_header):
    if not (auth_header and auth_header.startswith('Bearer ')):
        logger.error('No authorization token provided to preview service callback.')
        return False

    header_fields = auth_header[7:].split(':', 1)
    if len(header_fields) != 2:
        logger.error('Invalid authorization token provided to preview service callback.')
        return False

    nonce = to_int(header_fields[0]) or 0
    now = int(utc_now().timestamp() * 1000)
    if abs(now - nonce) > (600 * 1000):
        logger.error(f'Invalid authorization nonce provided to preview service callback: {nonce}.')
        return False

    if generate_preview_service_signature(str(nonce)) != auth_header:
        logger.error(f'Invalid authorization signature provided to preview service callback: {nonce}.')
        return False

    return True


def _byte_string(s):
    return bytes(s, 'utf-8')
