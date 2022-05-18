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

from time import sleep

from sqlalchemy import text
from squiggy import db
from squiggy.lib.background_job import BackgroundJob
from squiggy.lib.login_session import LoginSession
from squiggy.lib.previews import generate_whiteboard_preview
from squiggy.logger import initialize_background_logger, logger
from squiggy.models.whiteboard import Whiteboard


def launch_whiteboard_preview_generator():
    WhiteboardPreviewGenerator().launch()


class WhiteboardPreviewGenerator(BackgroundJob):

    whiteboard_id_queue = set()
    whiteboard_preview_generator = None

    def __init__(self, **kwargs):
        thread_name = 'whiteboard_preview_generator'
        self.logger = initialize_background_logger(
            name=thread_name,
            location='whiteboard_preview_generator.log',
        )
        self.is_running = False
        super().__init__(thread_name=thread_name, **kwargs)

    def launch(self):
        if not self.whiteboard_preview_generator:
            logger.info('Launching whiteboard preview generator')
        WhiteboardPreviewGenerator.start()

    def run(self):
        while True:
            if not self.is_running:
                self.is_running = True
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
                        generate_whiteboard_preview(whiteboard=whiteboard)
                    else:
                        self.logger.error(f'Whiteboard {whiteboard_id} gets no preview because instructor not found.')
                # This iteration is done
                self.is_running = False
            sleep(15)

    @classmethod
    def start(cls):
        cls.whiteboard_preview_generator = WhiteboardPreviewGenerator()
        cls.whiteboard_preview_generator.run_async()

    @classmethod
    def queue(cls, whiteboard_id):
        cls.whiteboard_id_queue.add(whiteboard_id)
