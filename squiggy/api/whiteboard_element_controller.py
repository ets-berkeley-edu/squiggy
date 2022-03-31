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

from flask import current_app as app, request
from flask_login import current_user, login_required
from squiggy.api.api_util import feature_flag_whiteboards
from squiggy.api.api_whiteboard_util import create_whiteboard_elements, update_whiteboard_elements
from squiggy.lib.http import tolerant_jsonify


@app.route('/api/whiteboard/elements/create', methods=['POST'])
@feature_flag_whiteboards
@login_required
def whiteboard_elements_create():
    params = request.get_json()
    whiteboard_elements = create_whiteboard_elements(
        user=current_user,
        whiteboard_id=params.get('whiteboardId'),
        whiteboard_elements=params.get('whiteboardElements'),
    )
    return tolerant_jsonify([e.to_api_json() for e in whiteboard_elements])


@app.route('/api/whiteboard/elements/update', methods=['POST'])
@feature_flag_whiteboards
@login_required
def whiteboard_elements_update():
    params = request.get_json()
    whiteboard_elements = update_whiteboard_elements(
        user=current_user,
        whiteboard_id=params.get('whiteboardId'),
        whiteboard_elements=params.get('whiteboardElements'),
    )
    return tolerant_jsonify([e.to_api_json() for e in whiteboard_elements])
