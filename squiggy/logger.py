"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

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


import logging
from logging.handlers import RotatingFileHandler
from threading import current_thread


def initialize_app_logger(app):
    from werkzeug.serving import WSGIRequestHandler

    # Configure app and library loggers.
    loggers = [app.logger]
    third_parties = [
        'boto3',
        'botocore',
        's3transfer',
        'socketio',
        'socketio.server',
        'sqlalchemy.engine',
        'werkzeug',
    ]
    for third_party in third_parties:
        loggers.append(logging.getLogger(third_party))

    # Capture runtime warnings so that we'll see them.
    logging.captureWarnings(True)

    # If location is configured as "STDOUT", don't create a new log file.
    location = app.config['LOGGING_LOCATION']
    if location == 'STDOUT':
        handlers = app.logger.handlers
    else:
        file_handler = RotatingFileHandler(location, mode='a', maxBytes=1024 * 1024 * 100, backupCount=20)
        handlers = [file_handler]

    for handler in handlers:
        handler.setLevel(app.config['LOGGING_LEVEL'])
        formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        handler.setFormatter(formatter)

    for logger in loggers:
        logger.handlers = []
        for handler in handlers:
            logger.addHandler(handler)
        if 'sqlalchemy' in logger.name:
            logger.setLevel(app.config['LOGGING_LEVEL_SQLALCHEMY'])
        elif logger.name in third_parties:
            logger.setLevel(app.config['LOGGING_PROPAGATION_LEVEL'])
        else:
            logger.setLevel(app.config['LOGGING_LEVEL'])

    def address_string(self):
        forwarded_for = self.headers.get('X-Forwarded-For')
        forwarded_for = forwarded_for.split(',')[0] if forwarded_for else None
        return forwarded_for or self.client_address[0]
    WSGIRequestHandler.address_string = address_string


def initialize_background_logger(name, location):
    from flask import current_app as app
    level = app.config['LOGGING_LEVEL']
    file_handler = RotatingFileHandler(location, mode='a', maxBytes=1024 * 1024 * 100, backupCount=20)
    handlers = [file_handler]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    for handler in handlers:
        handler.setLevel(level)
        formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class LogDelegator:

    def __getattr__(self, k):
        thread_name = current_thread().name
        if thread_name.startswith('poller-') or thread_name == 'whiteboard_housekeeping':
            delegate_logger = logging.getLogger(thread_name)
        else:
            from flask import current_app as app
            delegate_logger = app.logger
        return getattr(delegate_logger, k)


logger = LogDelegator()
