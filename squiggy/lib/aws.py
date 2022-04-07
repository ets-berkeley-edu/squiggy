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

from datetime import datetime
import re
from urllib.parse import parse_qs, urlparse

import boto3
from flask import current_app as app
import smart_open
from squiggy.logger import logger


S3_PREVIEW_URL_PATTERN = '^https://suitec-preview-images-\w+\.s3.*\.amazonaws\.com'


def get_s3_signed_url(url):
    if not is_s3_preview_url(url):
        return url
    parsed_url = urlparse(url)
    query_string = parse_qs(parsed_url.query)

    # If we already have a signed URL with at least an hour of life left, that will do.
    if 'Expires' in query_string and (int(query_string['Expires'][0]) - datetime.utcnow().timestamp()) > 3600:
        return url

    s3 = _get_s3_client()
    bucket = re.sub('\..*$', '', parsed_url.hostname)
    key = re.sub('^/', '', parsed_url.path)

    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key,
        },
        ExpiresIn=3600,
    )


def put_binary_data_to_s3(bucket, key, binary_data, content_type):
    try:
        s3 = _get_s3_client()
        s3.put_object(Body=binary_data, Bucket=bucket, Key=key, ContentType=content_type)
        return True
    except Exception as e:
        logger.error(f'S3 put operation failed (bucket={bucket}, key={key})')
        logger.exception(e)
        return None


def stream_object(s3_url):
    try:
        return smart_open.open(s3_url, 'rb', transport_params={'session': _get_session()})
    except Exception as e:
        logger.error(f'S3 stream operation failed (s3_url={s3_url})')
        logger.exception(e)
        return None


def is_s3_preview_url(url):
    return url and re.compile(S3_PREVIEW_URL_PATTERN).match(url)


def _get_s3_client():
    return _get_session().client('s3')


def _get_session():
    return boto3.Session(
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    )
