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

from squiggy.lib.util import is_admin, is_observer, is_student, is_teaching
from squiggy.models.user import User


class LoginSession:

    user = None

    def __init__(self, user_id):
        user = User.find_by_id(user_id) if user_id else None
        is_authorized = user and (is_admin(user) or user.canvas_enrollment_state != 'inactive')
        self.user = user if is_authorized else None

    def get_id(self):
        return self.user and self.user.id

    @property
    def canvas_course_role(self):
        return self.user and self.user.canvas_course_role

    @property
    def course(self):
        return self.user and self.user.course

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_admin(self):
        return is_admin(self)

    @property
    def is_observer(self):
        return is_observer(self)

    @property
    def is_student(self):
        return is_student(self)

    @property
    def is_authenticated(self):
        return self.user is not None

    @property
    def is_teaching(self):
        return is_teaching(self)

    @property
    def user_id(self):
        return self.user and self.user.id

    def logout(self):
        self.user = None

    def to_api_json(self):
        return {
            **(self.user.to_api_json(include_points=True, include_sharing=True) if self.user else {}),
            **{
                'course': self.course and self.course.to_api_json(),
                'isAdmin': self.is_admin,
                'isAuthenticated': self.is_authenticated,
                'isObserver': self.is_observer,
                'isStudent': self.is_student,
                'isTeaching': self.is_teaching,
            },
        }
