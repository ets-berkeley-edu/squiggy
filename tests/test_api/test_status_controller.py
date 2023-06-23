"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from datetime import timedelta

from squiggy import db, std_commit
from squiggy.lib.util import utc_now
from squiggy.lib.whiteboard_housekeeping import update_timestamp
from squiggy.models.canvas import Canvas
from squiggy.models.course import Course


class TestStatusController:
    """Status API."""

    def test_ping(self, client):
        """Answers the phone when pinged."""
        # Set up course
        canvas = db.session.query(Canvas).first()
        course = Course(
            active=True,
            canvas_api_domain=canvas.canvas_api_domain,
            canvas_course_id=9999999,
        )
        db.session.add(course)
        std_commit(allow_test_environment=True)

        def _ping(expected_ping_value):
            response = client.get('/api/ping')
            assert response.status_code == 200
            assert response.json['app'] is True
            assert response.json['cache'] is False
            assert response.json['db'] is True
            assert response.json['previewService'] is False
            assert response.json['poller'] is expected_ping_value
            assert response.json['whiteboards'] is expected_ping_value

        for minutes_ago in [59, 61]:
            the_past = utc_now() - timedelta(minutes=minutes_ago)
            course.last_polled = the_past
            db.session.add(course)
            update_timestamp(the_past)
            std_commit(allow_test_environment=True)
            _ping(minutes_ago < 60)

        # Teardown
        db.session.execute(f'DELETE FROM courses WHERE id = {course.id}')
        db.session.execute('DELETE FROM background_jobs')
        std_commit(allow_test_environment=True)
