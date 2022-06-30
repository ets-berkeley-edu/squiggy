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
import re

from flask import current_app as app
from squiggy.lib import http
from squiggy.lib.aws import upload_to_s3
from squiggy.lib.util import local_now, to_int, utc_now
from squiggy.lib.whiteboard_util import to_png_file
from squiggy.logger import logger


def generate_previews(object_id, object_url, object_type='asset'):
    if not app.config['PREVIEWS_ENABLED']:
        return True
    api_prefix = app.config['PREVIEWS_CALLBACK_API_PREFIX'] or app.config['API_PREFIX']
    post_back_urls = {
        'asset': f'{api_prefix}/previews/callback',
        'whiteboard': f'{api_prefix}/previews/whiteboard/callback',
    }
    response = http.request(
        app.config['PREVIEWS_URL'],
        headers={'authorization': generate_preview_service_signature()},
        method='post',
        data={
            'id': object_id,
            'url': object_url,
            'postBackUrl': post_back_urls[object_type],
        },
    )
    if not response:
        logger.error(f"""Failed to generate preview:
            object_type = {object_type}
            object_id = {object_id}
            object_url = {object_url}
        """)
    return response


def generate_preview_service_signature(nonce=None):
    if not nonce:
        nonce = str(int(utc_now().timestamp() * 1000))
    digester = hmac.new(_byte_string(app.config['PREVIEWS_API_KEY']), _byte_string(nonce), hashlib.sha1)
    return f"Bearer {nonce}:{base64.b64encode(digester.digest()).decode('utf-8')}"


def generate_whiteboard_preview(whiteboard):
    if app.config['PREVIEWS_ENABLED']:
        png_file = to_png_file(whiteboard)
        now = local_now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(png_file.name, mode='rb') as f:
            filename = re.sub(r'[^a-zA-Z0-9]', '_', whiteboard['title'])
            s3_attrs = upload_to_s3(
                byte_stream=f.read(),
                filename=f'{filename}_{now}.png',
                s3_key_prefix=get_s3_key_prefix(whiteboard['courseId'], 'whiteboard'),
            )
            if not generate_previews(
                object_id=whiteboard['id'],
                object_type='whiteboard',
                object_url=s3_attrs['download_url'],
            ):
                # TODO: If preview-image status is needed then the 'whiteboards' table needs 'preview_status' column.
                pass


def get_s3_key_prefix(course_id, object_type):
    # S3 key begins with course id, reversed for performant key distribution, padded for readability.
    return {
        'asset': f"{str(course_id)[::-1].rjust(7, '0')}/assets",
        'whiteboard': f"{str(course_id)[::-1].rjust(7, '0')}/whiteboard",
    }[object_type]


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
