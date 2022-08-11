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

from flask import current_app as app
from sqlalchemy.dialects.postgresql import ENUM
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.base import Base


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
    'get_whiteboard_add_asset',
    'get_whiteboard_remix',
    'whiteboard_add_asset',
    'whiteboard_export',
    'whiteboard_remix',
    name='enum_activities_type',
    create_type=False,
)


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

    @classmethod
    def get_activity_type_configuration(cls, course_id):
        def _default_configurations():
            feature_flag = app.config['FEATURE_FLAG_WHITEBOARDS']
            if feature_flag:
                return DEFAULT_ACTIVITY_TYPE_CONFIGURATION
            else:
                return list(filter(lambda c: 'whiteboard' not in c['type'], DEFAULT_ACTIVITY_TYPE_CONFIGURATION))
        activity_configs = []
        per_course_configs = cls.query.filter_by(course_id=course_id).all()
        for default_config in _default_configurations():
            activity_config = default_config.copy()
            per_course_config = next((c for c in per_course_configs if c.activity_type == activity_config['type']), None)
            if per_course_config:
                activity_config['enabled'] = per_course_config.enabled
                activity_config['points'] = per_course_config.points
            activity_configs.append(activity_config)
        std_commit()
        return activity_configs

    @classmethod
    def update_activity_type_configuration(cls, course_id, updates):
        existing_configs = cls.query.filter_by(course_id=course_id).all()
        for update in updates:
            existing_config = next((c for c in existing_configs if c.activity_type == update['type']), None)
            if existing_config:
                existing_config.enabled = update['enabled']
                existing_config.points = update['points']
                db.session.add(existing_config)
            else:
                new_config = cls(
                    activity_type=update['type'],
                    course_id=course_id,
                    enabled=update['enabled'],
                    points=update['points'],
                )
                db.session.add(new_config)
        std_commit()
        return True

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


DEFAULT_ACTIVITY_TYPE_CONFIGURATION = [
    {
        'type': 'asset_add',
        'title': 'Add a new asset to the Asset Library',
        'points': 5,
        'enabled': True,
    },
    {
        'type': 'asset_comment',
        'title': 'Comment on an asset in the Asset Library',
        'points': 3,
        'enabled': True,
    },
    {
        'type': 'asset_like',
        'title': 'Like an asset in the Asset Library',
        'points': 1,
        'enabled': True,
    },
    {
        'type': 'asset_view',
        'title': 'View an asset in the Asset Library',
        'points': 0,
        'enabled': True,
    },
    {
        'type': 'assignment_submit',
        'title': 'Submit a new assignment in Assignments',
        'points': 20,
        'enabled': True,
    },
    {
        'type': 'discussion_entry',
        'title': 'Add an entry on a topic in Discussions',
        'points': 3,
        'enabled': True,
    },
    {
        'type': 'discussion_topic',
        'title': 'Add a new topic in Discussions',
        'points': 5,
        'enabled': True,
    },
    {
        'type': 'get_asset_comment',
        'title': 'Receive a comment in the Asset Library',
        'points': 1,
        'enabled': True,
    },
    {
        'type': 'get_asset_comment_reply',
        'title': 'Receive a reply on a comment in the Asset Library',
        'points': 1,
        'enabled': True,
    },
    {
        'type': 'get_asset_like',
        'title': 'Receive a like in the Asset Library',
        'points': 1,
        'enabled': True,
    },
    {
        'type': 'get_asset_view',
        'title': 'Receive a view in the Asset Library',
        'points': 0,
        'enabled': True,
    },
    {
        'type': 'get_discussion_entry_reply',
        'title': 'Receive a reply on an entry in Discussions',
        'points': 1,
        'enabled': True,
    },
    {
        'type': 'whiteboard_add_asset',
        'title': 'Add an asset to a whiteboard',
        'points': 8,
        'enabled': True,
    },
    {
        'type': 'whiteboard_export',
        'title': 'Export a whiteboard to the Asset Library',
        'points': 10,
        'enabled': True,
    },
    {
        'type': 'get_whiteboard_add_asset',
        'title': 'Have one\'s asset added to a whiteboard',
        'points': 0,
        'enabled': True,
    },
    {
        'type': 'get_whiteboard_remix',
        'title': 'Have one\'s whiteboard remixed',
        'points': 0,
        'enabled': True,
    },
    {
        'type': 'whiteboard_remix',
        'title': 'Remix a whiteboard',
        'points': 0,
        'enabled': True,
    },
]
