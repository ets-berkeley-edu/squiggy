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

from dateutil.tz import tzutc
from squiggy import db, std_commit
from squiggy.models.base import Base


class Category(Base):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    canvas_assignment_id = db.Column(db.Integer)
    canvas_assignment_name = db.Column(db.String(255), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    deleted_at = db.Column(db.DateTime)
    title = db.Column(db.String(255), nullable=False)
    visible = db.Column(db.Boolean, nullable=True)

    def __init__(
            self,
            canvas_assignment_name,
            course_id,
            title,
            canvas_assignment_id=None,
            visible=True,
    ):
        self.canvas_assignment_id = canvas_assignment_id
        self.canvas_assignment_name = canvas_assignment_name
        self.course_id = course_id
        self.title = title
        self.visible = visible

    def __repr__(self):
        return f"""<Category
                    id={self.id},
                    canvas_assignment_id={self.canvas_assignment_id},
                    canvas_assignment_name={self.canvas_assignment_name},
                    course_id={self.course_id},
                    deleted_at={self.deleted_at},
                    title={self.title},
                    visible={self.visible},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    @classmethod
    def create(
            cls,
            canvas_assignment_name,
            course_id,
            title,
            canvas_assignment_id=None,
            visible=True,
    ):
        category = cls(
            canvas_assignment_name=canvas_assignment_name,
            course_id=course_id,
            title=title,
            canvas_assignment_id=canvas_assignment_id,
            visible=visible,
        )
        db.session.add(category)
        std_commit()
        return category

    @classmethod
    def get_categories_by_course_id(cls, course_id):
        return cls.query.filter_by(course_id=course_id).all()

    @classmethod
    def find_by_id(cls, category_id):
        return cls.query.filter_by(id=category_id).first()

    def to_api_json(self):
        return {
            'id': self.id,
            'canvas_assignment_id': self.canvas_assignment_id,
            'canvas_assignment_name': self.canvas_assignment_name,
            'course_id': self.course_id,
            'deleted_at': _isoformat(self.deleted_at),
            'title': self.title,
            'visible': self.visible,
            'createdAt': _isoformat(self.created_at),
            'updatedAt': _isoformat(self.updated_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
