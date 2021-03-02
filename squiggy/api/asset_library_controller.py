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

import json

from flask import current_app as app, request
from flask_login import login_required
from squiggy.lib.http import tolerant_jsonify


@app.route('/api/<domain>/<course_site_id>/assets')
@login_required
def assets(domain, course_site_id):
    args = {
        'category': _get(request.args, 'category', 0),
        'hasComments': _get(request.args, 'hasComments', 0),
        'hasImpact': _get(request.args, 'hasImpact', 0),
        'hasLikes': _get(request.args, 'hasLikes', 0),
        'hasPins': _get(request.args, 'hasPins', 0),
        'hasTrending': _get(request.args, 'hasTrending', 0),
        'hasViews': _get(request.args, 'hasViews', 0),
        'keywords': _get(request.args, 'keywords', 0),
        'limit': _get(request.args, 'limit', 0),
        'offset': _get(request.args, 'offset', 0),
        'searchContext': _get(request.args, 'searchContext', 0),
        'section': _get(request.args, 'section', 0),
        'sort': _get(request.args, 'sort', 0),
        'type': _get(request.args, 'type', 0),
        'user': _get(request.args, 'user', 0),
    }
    mock_json = _load_json(f'fixtures/mock_data_source/assets-{domain}-{course_site_id}.json')
    mock_json['offset'] = args['offset']
    return tolerant_jsonify(mock_json)


def _get(_dict, key, default_value=None):
    return _dict[key] if key in _dict else default_value


def _load_json(path):
    try:
        file = open(f"{app.config['BASE_DIR']}/{path}")
        return json.load(file)
    except (FileNotFoundError, KeyError, TypeError):
        return None
