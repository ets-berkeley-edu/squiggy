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

from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.activity import activities_type
from squiggy.models.base import Base


class ActivityType(Base):
    __tablename__ = 'activity_types'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    activity_type = db.Column('type', activities_type, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    points = db.Column(db.Integer)

    def __init__(
            self,
            activity_type,
            course_id,
            enabled=True,
            points=None,
    ):
        self.activity_type = activity_type
        self.course_id = course_id
        self.enabled = enabled
        self.points = points

    def __repr__(self):
        return f"""<ActivityType
                    type={self.activity_type},
                    course_id={self.course_id},
                    enabled={self.enabled},
                    points={self.points}>
                """

    @classmethod
    def create(cls, activity_type, course_id, enabled=True, points=None):
        activity_type_instance = cls(
            activity_type=activity_type,
            course_id=course_id,
            enabled=enabled,
            points=points,
        )
        db.session.add(activity_type_instance)
        std_commit()
        return activity_type_instance

    def to_api_json(self):
        return {
            'id': self.id,
            'type': self.activity_type,
            'courseId': self.course_id,
            'enabled': self.enabled,
            'points': self.points,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }
