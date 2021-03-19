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

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from squiggy import db, std_commit
from squiggy.lib.util import isoformat, to_int
from squiggy.models.base import Base
from squiggy.models.course import Course


canvas_enrollment_state_type = ENUM(
    'active',
    'completed',
    'inactive',
    'invited',
    'rejected',
    name='enum_users_canvas_enrollment_state',
    create_type=False,
)


class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    canvas_course_role = db.Column(db.String(255), nullable=False)
    canvas_course_sections = db.Column(ARRAY(db.String(255)))
    canvas_email = db.Column(db.String(255))
    canvas_enrollment_state = db.Column('canvas_enrollment_state', canvas_enrollment_state_type, nullable=False)
    canvas_full_name = db.Column(db.String(255), nullable=False)
    canvas_image = db.Column(db.String(255))
    canvas_user_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    share_points = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.now)

    course = db.relationship(Course.__name__, back_populates='users')

    def __init__(
        self,
        canvas_course_role,
        canvas_enrollment_state,
        canvas_full_name,
        canvas_user_id,
        course_id,
        canvas_course_sections=None,
        canvas_email=None,
        canvas_image=None,
        points=0,
        share_points=False,
    ):
        self.canvas_course_role = canvas_course_role
        self.canvas_course_sections = canvas_course_sections
        self.canvas_email = canvas_email
        self.canvas_enrollment_state = canvas_enrollment_state
        self.canvas_full_name = canvas_full_name
        self.canvas_image = canvas_image
        self.canvas_user_id = canvas_user_id
        self.course_id = course_id
        self.points = points
        self.share_points = share_points

    def __repr__(self):
        return f"""<User
                    canvas_course_role={self.canvas_course_role},
                    canvas_course_sections={self.canvas_course_sections},
                    canvas_email={self.canvas_email},
                    canvas_enrollment_state={self.canvas_enrollment_state},
                    canvas_full_name={self.canvas_full_name},
                    canvas_user_id={self.canvas_user_id},
                    course_id={self.course_id},
                    last_activity={self.last_activity},
                    points={self.points},
                    share_points={self.share_points},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    @classmethod
    def create(
            cls,
            canvas_course_role,
            canvas_enrollment_state,
            canvas_full_name,
            canvas_user_id,
            course_id,
            canvas_image=None,
            canvas_email=None,
            canvas_course_sections=None,
    ):
        user = cls(
            canvas_course_role=canvas_course_role,
            canvas_course_sections=canvas_course_sections,
            canvas_email=canvas_email,
            canvas_enrollment_state=canvas_enrollment_state,
            canvas_full_name=canvas_full_name,
            canvas_image=canvas_image,
            canvas_user_id=canvas_user_id,
            course_id=course_id,
        )
        db.session.add(user)
        std_commit()
        return user

    @classmethod
    def find_or_create(
            cls,
            canvas_course_role,
            canvas_enrollment_state,
            canvas_full_name,
            canvas_user_id,
            course_id,
            canvas_course_sections=None,
            canvas_email=None,
            canvas_image=None,
    ):
        where_clause = and_(
            cls.course_id == course_id,
            cls.canvas_user_id == canvas_user_id,
        )
        user = cls.query.filter(where_clause).one_or_none()
        if not user:
            user = cls(
                canvas_course_role=canvas_course_role,
                canvas_course_sections=canvas_course_sections,
                canvas_email=canvas_email,
                canvas_enrollment_state=canvas_enrollment_state,
                canvas_full_name=canvas_full_name,
                canvas_image=canvas_image,
                canvas_user_id=canvas_user_id,
                course_id=course_id,
            )
            db.session.add(user)
            std_commit()
        return user

    @classmethod
    def get_users_by_course_id(cls, course_id):
        return cls.query.filter_by(course_id=course_id).order_by(cls.canvas_full_name).all()

    @classmethod
    def find_by_id(cls, user_id):
        user_id = to_int(user_id)
        if not user_id:
            return None
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def find_by_ids(cls, user_ids):
        return cls.query.filter(cls.id.in_(user_ids)).all()

    def to_api_json(self):
        return {
            'id': self.id,
            'canvasUserId': self.canvas_user_id,
            'canvasCourseRole': self.canvas_course_role,
            'canvasCourseSections': self.canvas_course_sections,
            'canvasEmail': self.canvas_email,
            'canvasFullName': self.canvas_full_name,
            'canvasImage': self.canvas_image,
            'points': self.points,
            'sharePoints': self.share_points,
            'lastActivity': isoformat(self.last_activity),
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }
