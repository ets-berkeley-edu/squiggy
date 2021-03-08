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

from squiggy.models.authorized_user import AuthorizedUser
from squiggy.models.course import Course


class LoginSession:

    course = None
    session_id = None
    user = None

    def __init__(self, session_id):
        self.session_id = session_id
        ids = session_id.split(':') if ':' in (session_id or '') else []
        if len(ids) == 3:
            uid = ids[0]
            self.user = AuthorizedUser.find_by_uid(uid=uid)
            if self.user:
                canvas_api_domain = ids[1]
                canvas_course_id = ids[2]
                self.course = Course.find_by_canvas_course_id(canvas_api_domain, canvas_course_id)

    def get_id(self):
        return self.session_id

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_admin(self):
        # Non-admin users will be stored in a separate "Users" table keyed by Canvas id.
        return self.is_authenticated

    @property
    def is_authenticated(self):
        return self.user is not None

    def to_api_json(self):
        return {
            'course': self.course and self.course.to_api_json(),
            'isAdmin': self.is_admin,
            'isAuthenticated': self.is_authenticated,
            'isTeaching': False,  # TODO
            'uid': self.user and self.user.uid,
        }
