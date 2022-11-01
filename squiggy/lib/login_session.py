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

from sqlalchemy.sql import text
from squiggy import db
from squiggy.lib.util import is_admin, is_observer, is_student, is_teaching
from squiggy.models.user import User


class LoginSession:

    api_json = None
    user_id = None

    def __init__(self, user_id):
        self.user_id = user_id
        self.refresh()

    def get_id(self):
        return self._get('id')

    @property
    def asset_ids(self):
        sql = 'SELECT asset_id FROM asset_users WHERE user_id = :id'
        rows = db.session.execute(text(sql), {'id': self.id}).all()
        return [row['asset_id'] for row in rows]

    @property
    def canvas_course_role(self):
        return self._get('canvasCourseRole')

    @property
    def course_id(self):
        return self._get('course.id')

    @property
    def canvas_api_domain(self):
        return self._get('course.canvasApiDomain')

    @property
    def canvas_course_id(self):
        return self._get('course.canvasCourseId')

    @property
    def canvas_course_sections(self):
        return self._get('canvasCourseSections')

    @property
    def id(self):  # noqa: A003
        return self.get_id()

    @property
    def is_active(self):
        return self._get('isAuthenticated')

    @property
    def is_admin(self):
        return self._get('isAdmin')

    @property
    def is_observer(self):
        return self._get('isObserver')

    @property
    def is_student(self):
        return self._get('isStudent')

    @property
    def is_authenticated(self):
        return self._get('isAuthenticated')

    @property
    def is_teaching(self):
        return self._get('isTeaching')

    @property
    def protect_assets_per_section(self):
        return self.is_student and self._get('course.protectsAssetsPerSection')

    def refresh(self):
        user = User.find_by_id(self.user_id) if self.user_id else None
        self.api_json = _construct_api_json(user)

    def to_api_json(self):
        return self.api_json

    def _get(self, nested_property_reference):
        if nested_property_reference in [
            'assets',
            'canvasGroups',
            'course',
            'course.active',
            'course.canvasGroups'
            'course.protectsAssetsPerSection',
            'lastActivity',
            'lookingForCollaborators',
            'points',
            'sharePoints',
            'updatedAt',
            'whiteboards',
        ]:
            raise ValueError(f'Referencing {nested_property_reference} (volatile data) in session object not allowed.')
        value = None
        keys = nested_property_reference.split('.')
        for index, key in enumerate(keys):
            if index == 0:
                value = self.api_json.get(key)
            elif isinstance(value, dict):
                value = value.get(key)
            else:
                raise ValueError(f'Non-dict object in current_user.{nested_property_reference}')
        return value

    def _logout(self):
        self.api_json = _construct_api_json()


def _construct_api_json(user=None):
    is_authenticated = user and (is_admin(user) or user.canvas_enrollment_state != 'inactive')
    api_json = {
        **(user.to_api_json(include_points=True, include_sharing=True) if is_authenticated else {}),
        **{
            'course': is_authenticated and user.course.to_api_json(),
            'isAdmin': is_authenticated and is_admin(user),
            'isAuthenticated': is_authenticated,
            'isObserver': is_authenticated and is_observer(user),
            'isStudent': is_authenticated and is_student(user),
            'isTeaching': is_authenticated and is_teaching(user),
        },
    }
    return api_json
