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

from argparse import Namespace
from queue import Queue
import time

from sqlalchemy import text
from squiggy import db
from squiggy.lib.background_job import BackgroundJob
from squiggy.lib.login_session import LoginSession
from squiggy.lib.previews import generate_whiteboard_preview
from squiggy.logger import initialize_background_logger, logger
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession


def launch_whiteboard_housekeeping():
    WhiteboardHousekeeping().launch()


class WhiteboardHousekeeping(BackgroundJob):

    whiteboard_id_queue = Queue()
    whiteboard_element_transaction_queue = Queue()
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
            epoch_time = int(time.time())
            if not self.is_running:
                self.is_running = True
                self._execute_whiteboard_element_transactions()
                if epoch_time % 15 == 0:
                    self._generate_whiteboard_previews()
                    WhiteboardSession.delete_stale_sessions()
                self.is_running = False

    def _generate_whiteboard_previews(self):
        while not self.whiteboard_id_queue.empty():
            whiteboard_id = self.whiteboard_id_queue.get()
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

    def _execute_whiteboard_element_transactions(self):
        while not self.whiteboard_element_transaction_queue.empty():
            transaction = Namespace(**self.whiteboard_element_transaction_queue.get())
            logger.debug(f'Queue whiteboard_elements transaction: {transaction}')
            if transaction.type == 'delete':
                for whiteboard_element in transaction.whiteboard_elements:
                    _delete_whiteboard_element(
                        is_student=transaction.is_student,
                        user_id=transaction.user_id,
                        socket_id=transaction.socket_id,
                        whiteboard_id=transaction.whiteboard_id,
                        whiteboard_element=whiteboard_element,
                    )
            elif transaction.type == 'upsert':
                # TODO
                pass
            else:
                raise ValueError(f'Invalid whiteboard_element transaction type: {transaction.type}')

    @classmethod
    def start(cls):
        cls.whiteboard_housekeeping = WhiteboardHousekeeping()
        cls.whiteboard_housekeeping.run_async()

    @classmethod
    def queue_for_preview_image(cls, whiteboard_id):
        cls.whiteboard_id_queue.put(whiteboard_id)

    @classmethod
    def queue_whiteboard_elements_transaction(
            cls,
            course_id,
            current_user_id,
            is_student,
            socket_id,
            transaction_type,
            whiteboard_elements,
            whiteboard_id,
    ):
        transaction = {
            'course_id': course_id,
            'is_student': is_student,
            'socket_id': socket_id,
            'type': transaction_type,
            'user_id': current_user_id,
            'whiteboard_elements': whiteboard_elements,
            'whiteboard_id': whiteboard_id,
        }
        cls.whiteboard_element_transaction_queue.put(transaction)


def _delete_whiteboard_element(
        is_student,
        socket_id,
        user_id,
        whiteboard_element,
        whiteboard_id,
):
    uuid = whiteboard_element['element']['uuid']
    whiteboard_element = WhiteboardElement.find_by_uuid(uuid=uuid, whiteboard_id=whiteboard_id)
    if whiteboard_element:
        if whiteboard_element.asset_id:
            AssetWhiteboardElement.delete(
                asset_id=whiteboard_element.asset_id,
                uuid=whiteboard_element.uuid,
            )
        WhiteboardElement.delete(uuid=uuid, whiteboard_id=whiteboard_id)
        WhiteboardHousekeeping.queue_for_preview_image(whiteboard_id)
        if is_student:
            WhiteboardSession.update_updated_at(
                socket_id=socket_id,
                user_id=user_id,
                whiteboard_id=whiteboard_id,
            )
