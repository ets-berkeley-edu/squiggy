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

from flask import current_app as app
from flask_login import login_required
from squiggy.lib.http import tolerant_jsonify


@app.route('/api/<domain>/<course_site_id>/categories')
@login_required
def categories(domain, course_site_id):
    return tolerant_jsonify([
        {
            'id': 21696,
            'title': 'Week 1',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.120Z',
            'updatedAt': '2021-01-13T23:02:03.120Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 145,
        },
        {
            'id': 21697,
            'title': 'Week 2',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.130Z',
            'updatedAt': '2021-01-13T23:02:03.130Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 112,
        },
        {
            'id': 21698,
            'title': 'Week 3',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.144Z',
            'updatedAt': '2021-01-13T23:02:03.144Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 135,
        },
        {
            'id': 21699,
            'title': 'Week 4',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.151Z',
            'updatedAt': '2021-01-13T23:02:03.151Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 151,
        },
        {
            'id': 21700,
            'title': 'Week 5',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.163Z',
            'updatedAt': '2021-01-13T23:02:03.164Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 119,
        },
        {
            'id': 21701,
            'title': 'Week 6',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.180Z',
            'updatedAt': '2021-01-13T23:02:03.180Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 62,
        },
        {
            'id': 21702,
            'title': 'Week 7',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.197Z',
            'updatedAt': '2021-01-13T23:02:03.197Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 54,
        },
        {
            'id': 21703,
            'title': 'Week 8',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.215Z',
            'updatedAt': '2021-01-13T23:02:03.216Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 81,
        },
        {
            'id': 21704,
            'title': 'Week 9',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.223Z',
            'updatedAt': '2021-01-13T23:02:03.224Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 63,
        },
        {
            'id': 21705,
            'title': 'Week 10',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.237Z',
            'updatedAt': '2021-01-13T23:02:03.238Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 36,
        },
        {
            'id': 21706,
            'title': 'Week 11',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.247Z',
            'updatedAt': '2021-01-13T23:02:03.247Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 45,
        },
        {
            'id': 21707,
            'title': 'Week 12',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.265Z',
            'updatedAt': '2021-01-13T23:02:03.265Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 36,
        },
        {
            'id': 21708,
            'title': 'Week 13',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.417Z',
            'updatedAt': '2021-01-13T23:02:03.417Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 18,
        },
        {
            'id': 21709,
            'title': 'Week 14',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.424Z',
            'updatedAt': '2021-01-13T23:02:03.424Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 27,
        },
        {
            'id': 21710,
            'title': 'Week 15',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.430Z',
            'updatedAt': '2021-01-13T23:02:03.430Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 0,
        },
        {
            'id': 21711,
            'title': 'Week 16',
            'canvasAssignmentId': None,
            'canvasAssignment_name': None,
            'createdAt': '2021-01-13T23:02:03.435Z',
            'updatedAt': '2021-01-13T23:02:03.435Z',
            'courseId': 2516,
            'deletedAt': None,
            'visible': True,
            'assetCount': 18,
        },
    ])
