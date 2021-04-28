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

from sqlalchemy import and_
from sqlalchemy.dialects.postgresql import ENUM, JSON
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.base import Base


activities_object_type = ENUM(
    'asset',
    'canvas_discussion',
    'canvas_submission',
    'comment',
    name='enum_activities_object_type',
    create_type=False,
)


activities_type = ENUM(
    'asset_add',
    'asset_comment',
    'asset_like',
    'asset_view',
    'assignment_submit',
    'discussion_entry',
    'discussion_topic',
    'get_asset_comment',
    'get_asset_comment_reply',
    'get_asset_like',
    'get_asset_view',
    'get_discussion_entry_reply',
    name='enum_activities_type',
    create_type=False,
)


class Activity(Base):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    activity_type = db.Column('type', activities_type, nullable=False)
    object_id = db.Column(db.Integer)
    object_type = db.Column('object_type', activities_object_type, nullable=False)
    activity_metadata = db.Column('metadata', JSON)
    asset_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    actor_id = db.Column(db.Integer)
    reciprocal_id = db.Column(db.Integer)

    user = db.relationship('User')

    def __init__(
        self,
        activity_type,
        course_id,
        user_id,
        object_type,
        object_id=None,
        asset_id=None,
        actor_id=None,
        reciprocal_id=None,
        activity_metadata=None,
    ):
        self.activity_type = activity_type
        self.course_id = course_id
        self.user_id = user_id
        self.object_type = object_type
        self.object_id = object_id
        self.asset_id = asset_id
        self.actor_id = actor_id
        self.reciprocal_id = reciprocal_id
        self.activity_metadata = activity_metadata

    def __repr__(self):
        return f"""<Activity
                    type={self.activity_type},
                    course_id={self.course_id},
                    user_id={self.user_id},
                    object_type={self.object_type}
                    object_id={self.object_id}
                    asset_id={self.asset_id}
                    actor_id={self.actor_id}
                    reciprocal_id={self.reciprocal_id}
                    metadata={self.activity_metadata}>
                """

    @classmethod
    def create(
        cls,
        activity_type,
        course_id,
        user_id,
        object_type,
        object_id=None,
        asset_id=None,
        actor_id=None,
        reciprocal_id=None,
        activity_metadata=None,
    ):
        activity = cls(
            activity_type=activity_type,
            course_id=course_id,
            user_id=user_id,
            object_type=object_type,
            object_id=object_id,
            asset_id=asset_id,
            actor_id=actor_id,
            reciprocal_id=reciprocal_id,
            activity_metadata=activity_metadata,
        )
        db.session.add(activity)
        std_commit()
        return activity

    @classmethod
    def create_unless_exists(cls, **kwargs):
        if cls.query.filter_by(**kwargs).count() == 0:
            return cls.create(**kwargs)

    @classmethod
    def delete_by_object_id(cls, object_type, object_id):
        cls.query.filter(and_(cls.object_type == object_type, cls.object_id == object_id)).delete()

    @classmethod
    def find_by_object_id(cls, object_type, object_id):
        return cls.query.filter(and_(cls.object_type == object_type, cls.object_id == object_id)).all()

    def to_api_json(self):
        return {
            'id': self.id,
            'activityType': self.activity_type,
            'courseId': self.course_id,
            'userId': self.user_id,
            'objectType': self.object_type,
            'objectId': self.object_id,
            'assetId': self.asset_id,
            'actorId': self.actor_id,
            'reciprocalId': self.reciprocal_id,
            'metadata': self.activity_metadata,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }
