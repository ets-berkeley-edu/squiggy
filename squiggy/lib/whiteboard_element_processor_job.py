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

from squiggy.api.whiteboard_socket_handler import upsert_whiteboard_element
from squiggy.lib.background_job import BackgroundJob
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.logger import initialize_background_logger, logger
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession


def launch_whiteboard_element_processor():
    WhiteboardElementProcessor().launch()


class WhiteboardElementProcessor(BackgroundJob):

    whiteboard_element_processor = None
    whiteboard_element_transaction_queue = Queue(maxsize=-1)

    def __init__(self, **kwargs):
        thread_name = 'whiteboard_element_processor'
        self.logger = initialize_background_logger(
            name=thread_name,
            location='whiteboard_element_processor.log',
        )
        self.is_running = False
        super().__init__(thread_name=thread_name, **kwargs)

    def launch(self):
        if not self.whiteboard_element_processor:
            logger.info('Launching whiteboard_element_processor')
        WhiteboardElementProcessor.start()

    def run(self):
        while True:
            if not self.is_running:
                self.is_running = True
                self._execute_whiteboard_element_transactions()
                self.is_running = False

    def _execute_whiteboard_element_transactions(self):
        while not self.whiteboard_element_transaction_queue.empty():
            transaction = Namespace(**self.whiteboard_element_transaction_queue.get())
            if transaction.type == 'delete':
                for whiteboard_element in transaction.whiteboard_elements:
                    self.logger.info(f'Delete whiteboard_element where UUID = {whiteboard_element}')
                    _delete_whiteboard_element(
                        is_student=transaction.is_student,
                        user_id=transaction.user_id,
                        socket_id=transaction.socket_id,
                        whiteboard_id=transaction.whiteboard_id,
                        whiteboard_element=whiteboard_element,
                    )
            elif transaction.type == 'upsert':
                for whiteboard_element in transaction.whiteboard_elements:
                    self.logger.info(f'Upsert whiteboard_element where UUID = {whiteboard_element}')
                    upsert_whiteboard_element(
                        course_id=transaction.course_id,
                        is_student=transaction.is_student,
                        user_id=transaction.user_id,
                        socket_id=transaction.socket_id,
                        whiteboard_id=transaction.whiteboard_id,
                        whiteboard_element=whiteboard_element,
                    )
                WhiteboardHousekeeping.queue_for_preview_image(transaction.whiteboard_id)
            else:
                raise ValueError(f'Invalid whiteboard_element transaction type: {transaction.type}')

    @classmethod
    def get_status(cls):
        if not cls.whiteboard_element_processor:
            return False
        return {
            'whiteboardElementTransactionQueue': {
                'isEmpty': cls.whiteboard_element_transaction_queue.empty(),
                'isFull': cls.whiteboard_element_transaction_queue.full(),
                'size': cls.whiteboard_element_transaction_queue.qsize(),
                'unfinished_tasks': cls.whiteboard_element_transaction_queue.unfinished_tasks,
            },
        }

    @classmethod
    def start(cls):
        cls.whiteboard_element_processor = WhiteboardElementProcessor()
        cls.whiteboard_element_processor.run_async()

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
