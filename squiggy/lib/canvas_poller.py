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
                .filter_by(canvas_api_domain=canvas_api_domain, active=True) \
                .order_by(nullsfirst(Course.last_polled.asc())) \
                .with_for_update() \
                .first()
            app.logger.info(f"Will poll {_format_course(course)}, last polled {course.last_polled or 'never'}")
            course.last_polled = datetime.now()
            db.session.add(course)
            std_commit()

            try:
                self.poll_course(course)
            except Exception as e:
                app.logger.error(f'Failed to poll course {_format_course(course)}')
                app.logger.exception(e)
            sleep(5)

    def poll_course(self, db_course):
        api_course = self.canvas.get_course(db_course.canvas_course_id)
        self.poll_tab_configuration(db_course, api_course)

    def poll_tab_configuration(self, db_course, api_course):
        tabs = api_course.get_tabs()
        course_updates = {}
        has_active_tools = False

        if db_course.asset_library_url:
            asset_library_tab = next((t for t in tabs if db_course.asset_library_url.endswith(t.html_url)), None)
            if not asset_library_tab or getattr(asset_library_tab, 'hidden', None):
                app.logger.info(f'No active tab found for Asset Library, will remove URL from db: {_format_course(db_course)}')
                course_updates['asset_library_url'] = None
            else:
                has_active_tools = True
        if db_course.engagement_index_url:
            engagement_index_tab = next((t for t in tabs if db_course.engagement_index_url.endswith(t.html_url)), None)
            if not engagement_index_tab or getattr(engagement_index_tab, 'hidden', None):
                app.logger.info(f'No active tab found for Engagement Index, will remove URL from db: {_format_course(db_course)}')
                course_updates['engagement_index_url'] = None
            else:
                has_active_tools = True

        if not has_active_tools:
            app.logger.info(f'No active tools found for course, will mark inactive: {_format_course(db_course)}')
            course_updates['active'] = False

        if course_updates:
            for key, value in course_updates.items():
                setattr(db_course, key, value)
                db.session.add(db_course)
            std_commit()


def _format_course(course):
    return f'course {course.canvas_course_id}, {course.canvas_api_domain}'
