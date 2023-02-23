"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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
from squiggy.models.base import Base


class CourseGroup(Base):
    __tablename__ = 'course_groups'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    canvas_group_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255))
    category_name = db.Column(db.String(255))

    course = db.relationship('Course', back_populates='groups')
    memberships = db.relationship('CourseGroupMembership', back_populates='course_group')

    def __init__(
        self,
        course_id,
        canvas_group_id,
        name,
        category_name,
    ):
        self.course_id = course_id
        self.canvas_group_id = canvas_group_id
        self.name = name
        self.category_name = category_name

    def __repr__(self):
        return f"""<CourseGroup
                    id={self.id},
                    course_id={self.course_id},
                    canvas_group_id={self.canvas_group_id},
                    name={self.name}
                    category_name={self.category_name}>
                """

    @classmethod
    def create(cls, course_id, canvas_group_id, name, category_name):
        course_group = cls(
            course_id=course_id,
            canvas_group_id=canvas_group_id,
            name=name,
            category_name=category_name,
        )
        db.session.add(course_group)
        std_commit()
        return course_group

    def to_api_json(self):
        return {
            'id': self.id,
            'canvasGroupId': self.canvas_group_id,
            'categoryName': self.category_name,
            'courseId': self.course_id,
            'name': self.name,
            'label': f'{self.category_name} - {self.name}',
        }
