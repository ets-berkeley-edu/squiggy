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

import json
import os
import subprocess
import sys
import tempfile

from flask import current_app as app
from squiggy import mock
from squiggy.logger import logger


@mock('fixtures/mock_whiteboard.png')
def to_png_file(whiteboard):
    base_dir = app.config['BASE_DIR']
    whiteboard_elements_file = tempfile.NamedTemporaryFile(suffix='.json').name
    with open(whiteboard_elements_file, mode='wt', encoding='utf-8') as f:
        elements = [w['element'] for w in whiteboard['whiteboardElements']]
        json.dump(elements, f)
    try:
        script = 'save_whiteboard_as_png.js'
        png_dir = os.path.dirname(os.path.realpath(whiteboard_elements_file))
        png_file = f'{png_dir}/whiteboard.png'
        executable = [
            app.config['NODE_EXECUTABLE'],
            f'{base_dir}/scripts/node_js/{script}',
            '-b',
            base_dir,
            '-w',
            whiteboard_elements_file,
            '-p',
            png_file,
        ]
        logger.info(f"""
            Execute whiteboard.to_png_file script:
            {executable}
        """)
        subprocess.Popen(executable, stdout=subprocess.PIPE).wait(timeout=200000)
        return png_file
    except OSError as e:
        app.logger.error(f"""
            OSError: {e.strerror}
            OSError number: {e.errno}
            OSError filename: {e.filename}
        """)
    except:  # noqa: E722
        app.logger.error(sys.exc_info()[0])
