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


ALERT_INFREQUENT_ACTIVITY_ENABLED = False
ALERT_WITHDRAWAL_ENABLED = False

AWS_APP_ROLE_ARN = 'arn:aws:iam::123456789012:role/test-role'

BOOKMARKLET_ENCRYPTION_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='

CANVAS_POLLER = False

DIST_STATIC_DIR = 'tests/static'

LOGGING_LOCATION = 'STDOUT'

PREVIEWS_ENABLED = False

SQLALCHEMY_DATABASE_URI = f"postgresql://squiggy:squiggy@localhost:{os.getenv('PGPORT', '5432')}/squiggy_test"

TESTING = True
