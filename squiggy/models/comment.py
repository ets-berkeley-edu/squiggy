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

from sqlalchemy.sql import desc
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.activity import Activity
from squiggy.models.base import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer)

    asset = db.relationship('Asset', back_populates='comments')
    user = db.relationship('User')

    def __init__(
            self,
            asset_id,
            user_id,
            body,
            parent_id=None,
    ):
        self.body = body
        self.asset_id = asset_id
        self.user_id = user_id
        self.parent_id = parent_id

    def __repr__(self):
        return f"""<Comment
                    asset_id={self.asset_id},
                    user_id={self.user_id},
                    parent_id={self.parent_id},
                    body={self.body}>
                """

    @classmethod
    def delete(cls, comment_id):
        comment = cls.query.filter_by(id=comment_id).first()
        if comment:
            asset = comment.asset
            db.session.delete(comment)
            Activity.delete_by_object_id(
                object_type='comment',
                object_id=comment_id,
                course_id=comment.asset.course_id,
                user_ids=[comment.user_id] + [u.id for u in comment.asset.users],
            )
            std_commit(allow_test_environment=True)
            if asset:
                asset.refresh_comments_count()

    @classmethod
    def find_by_id(cls, comment_id):
        return cls.query.filter_by(id=comment_id).first()

    @classmethod
    def create(cls, asset, user_id, body, parent_id=None):
        comment = cls(
            asset_id=asset.id,
            user_id=user_id,
            body=body,
            parent_id=parent_id,
        )
        db.session.add(comment)
        std_commit(allow_test_environment=True)
        _create_activities_per_new_comment(asset=asset, comment=comment)
        asset.refresh_comments_count()
        return comment

    @classmethod
    def update(cls, body, comment_id):
        comment = cls.find_by_id(comment_id)
        comment.body = body
        db.session.add(comment)
        std_commit()
        return comment

    @classmethod
    def get_comments(cls, asset_id):
        orphans = []
        parents = []
        # Sort reverse chronological
        order_by = desc(cls.created_at)
        for row in cls.query.filter_by(asset_id=asset_id).order_by(order_by).all():
            comment = row.to_api_json()
            (orphans if row.parent_id else parents).append(comment)
            comment['replies'] = []
        while len(orphans):
            orphan = orphans.pop(0)
            # Find the child's parent
            parent = next((c for c in (parents + orphans) if orphan['parentId'] == c['id']), None)
            if parent:
                parent['replies'].insert(0, orphan)
        return parents

    def to_api_json(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'parentId': self.parent_id,
            'body': self.body,
            'createdAt': isoformat(self.created_at),
            'updatedAt': isoformat(self.updated_at),
        }


def _create_activities_per_new_comment(asset, comment):
    if asset.visible:
        course_id = asset.course_id
        if comment.user_id not in [user.id for user in asset.users]:
            Activity.create(
                activity_type='asset_comment',
                course_id=course_id,
                user_id=comment.user_id,
                object_type='comment',
                object_id=comment.id,
                asset_id=asset.id,
            )
            for user in asset.users:
                Activity.create(
                    activity_type='get_asset_comment',
                    course_id=course_id,
                    user_id=user.id,
                    object_type='comment',
                    object_id=comment.id,
                    asset_id=asset.id,
                )
        if comment.parent_id:
            parent = Comment.find_by_id(comment.parent_id)
            if parent.user_id != comment.user_id:
                Activity.create(
                    activity_type='get_asset_comment_reply',
                    course_id=course_id,
                    user_id=parent.user_id,
                    object_type='comment',
                    object_id=parent.id,
                    asset_id=asset.id,
                )
