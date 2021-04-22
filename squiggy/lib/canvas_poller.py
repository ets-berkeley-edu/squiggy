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

from datetime import datetime
from time import sleep

from flask import current_app as app
from sqlalchemy import nullsfirst
from squiggy import db, std_commit
from squiggy.externals.canvas import get_canvas
from squiggy.lib.background_job import BackgroundJob
from squiggy.models.canvas_poller_api_key import CanvasPollerApiKey
from squiggy.models.course import Course


def launch_pollers():
    keys = CanvasPollerApiKey.query.all()
    app.logger.info(f'Will start {len(keys)} poller instances')
    for key in keys:
        CanvasPoller(canvas_api_domain=key.canvas_api_domain, api_key=key.api_key).run_async()


class CanvasPoller(BackgroundJob):

    def run(self, canvas_api_domain, api_key):
        app.logger.info(f'New poller running for {canvas_api_domain}')
        api_url = f'https://{canvas_api_domain}'
        self.canvas = get_canvas(api_url, api_key)

        while True:
            course = db.session.query(Course) \
                .filter_by(canvas_api_domain=canvas_api_domain) \
                .order_by(nullsfirst(Course.last_polled.asc())) \
                .with_for_update() \
                .first()
            app.logger.info(f"Will poll course {course.id}, {course.canvas_api_domain}, last polled {course.last_polled or 'never'}")
            course.last_polled = datetime.now()
            db.session.add(course)
            std_commit()

            self.poll_course(course.id)
            sleep(5)

    def poll_course(self, course_id):
        pass
