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


import os
from threading import Thread

from flask import current_app as app


"""Parent class for background jobs."""


class BackgroundJob(object):

    def __init__(self, **kwargs):
        self.job_args = kwargs

    def run(self, **kwargs):
        pass

    def run_async(self, **async_opts):
        if os.environ.get('SQUIGGY_ENV') in ['test', 'testext']:
            app.logger.info('Test run in progress; will not muddy the waters by actually kicking off a background thread.')
            return True
        app.logger.info('About to start background thread.')
        app_arg = app._get_current_object()
        self.job_args.update(async_opts)
        kwargs = self.job_args
        thread = Thread(target=self.run_in_app_context, args=[app_arg], kwargs=kwargs, daemon=True)
        thread.start()
        return True

    def run_in_app_context(self, app_arg, **kwargs):
        with app_arg.app_context():
            self.run_wrapped(**kwargs)

    def run_wrapped(self, **kwargs):
        try:
            result = self.run(**kwargs)
        except BackgroundJobError as e:
            app.logger.error(e)
            result = None
        except Exception as e:
            app.logger.exception(e)
            result = None
        return result


class BackgroundJobError(Exception):
    pass
