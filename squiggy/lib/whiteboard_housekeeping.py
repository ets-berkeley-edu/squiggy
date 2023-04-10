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

from time import sleep

from flask import current_app as app
from sqlalchemy import text
from squiggy import db
from squiggy.lib.background_job import BackgroundJob
from squiggy.lib.db_util import advisory_lock
from squiggy.lib.login_session import LoginSession
from squiggy.lib.previews import generate_whiteboard_preview
from squiggy.lib.util import utc_now
from squiggy.logger import initialize_background_logger, logger
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_session import WhiteboardSession


def launch_whiteboard_housekeeping():
    WhiteboardHousekeeping().launch()


class WhiteboardHousekeeping(BackgroundJob):

    whiteboard_id_queue = set()
    whiteboard_housekeeping = None

    def __init__(self, **kwargs):
        thread_name = 'whiteboard_housekeeping'
        self.logger = initialize_background_logger(
            name=thread_name,
            location='whiteboard_housekeeping.log',
        )
        self.is_running = False
        super().__init__(thread_name=thread_name, **kwargs)

    def launch(self):
        if not self.whiteboard_housekeeping:
            logger.info('Launching whiteboard preview generator')
        WhiteboardHousekeeping.start()

    def run(self):
        while True:
            if not self.is_running:
                with advisory_lock(app.config['ADVISORY_LOCK_ID_WHITEBOARD_HOUSEKEEPING']):
                    self.is_running = True
                    try:
                        self._generate_whiteboard_previews()
                        WhiteboardSession.delete_stale_sessions()
                    finally:
                        self.is_running = False
            sleep(15)

    def _generate_whiteboard_previews(self):
        # Copy and clear
        whiteboard_id_set = self.whiteboard_id_queue.copy()
        self.whiteboard_id_queue.clear()

        for whiteboard_id in whiteboard_id_set:
            # First, find user authorized to render whiteboard.
            sql = text("""
                SELECT u.id FROM users u
                JOIN whiteboards w ON w.course_id = u.course_id
                WHERE w.id = :whiteboard_id
                  AND (
                    u.canvas_course_role ILIKE '%admin%'
                    OR u.canvas_course_role ILIKE '%instructor%'
                    OR u.canvas_course_role ILIKE '%teacher%'
                )
                ORDER BY u.canvas_course_role LIMIT 1
            """)
            result = db.session.execute(sql, {'whiteboard_id': whiteboard_id}).fetchone()
            user_id = result[0] if result else None
            if user_id:
                # Next, generate whiteboard preview image.
                whiteboard = Whiteboard.find_by_id(
                    current_user=LoginSession(user_id),
                    whiteboard_id=whiteboard_id,
                )
                self.logger.info(f'Generating preview image for whiteboard {whiteboard_id}')
                image_url = generate_whiteboard_preview(whiteboard=whiteboard)
                if image_url:
                    Whiteboard.update_preview(
                        whiteboard_id=whiteboard['id'],
                        image_url=image_url,
                    )
            else:
                self.logger.error(f'Whiteboard {whiteboard_id} gets no preview because instructor not found.')

        update_timestamp(utc_now())
        self.logger.info('Generation job cycle complete, updated timestamp.')

    @classmethod
    def start(cls):
        cls.whiteboard_housekeeping = WhiteboardHousekeeping()
        cls.whiteboard_housekeeping.run_async()

    @classmethod
    def queue_for_preview_image(cls, whiteboard_id):
        cls.whiteboard_id_queue.add(whiteboard_id)


def update_timestamp(time):
    update_timestamp_sql = text("""
        INSERT INTO background_jobs (job_name, last_run)
        VALUES('whiteboard_housekeeping', now())
        ON CONFLICT (job_name) DO
        UPDATE SET last_run = :time
    """)
    db.session.execute(update_timestamp_sql, {'time': time})
