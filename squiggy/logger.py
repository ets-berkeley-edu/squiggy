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


import logging
from logging.handlers import RotatingFileHandler
from threading import current_thread


def initialize_app_logger(app):
    level = app.config['LOGGING_LEVEL']
    location = app.config['LOGGING_LOCATION']
    log_propagation_level = app.config['LOGGING_PROPAGATION_LEVEL']

    # Configure app and library loggers.
    loggers = [
        app.logger,
        logging.getLogger('werkzeug'),
    ]

    # Capture runtime warnings so that we'll see them.
    logging.captureWarnings(True)

    # If location is configured as "STDOUT", don't create a new log file.
    if location == 'STDOUT':
        handlers = app.logger.handlers
    else:
        file_handler = RotatingFileHandler(location, mode='a', maxBytes=1024 * 1024 * 100, backupCount=20)
        handlers = [file_handler]

    for handler in handlers:
        handler.setLevel(level)
        formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        handler.setFormatter(formatter)

    for logger in loggers:
        logger.handlers = []
        for handler in handlers:
            logger.addHandler(handler)
        logger.setLevel(level)

    logging.getLogger('boto3').setLevel(log_propagation_level)
    logging.getLogger('botocore').setLevel(log_propagation_level)
    logging.getLogger('s3transfer').setLevel(log_propagation_level)


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
        if thread_name.startswith('poller-'):
            delegate_logger = logging.getLogger(thread_name)
        else:
            from flask import current_app as app
            delegate_logger = app.logger
        return getattr(delegate_logger, k)


logger = LogDelegator()
