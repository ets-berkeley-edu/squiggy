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

from squiggy import db, std_commit
from squiggy.lib.util import db_row_to_dict, isoformat, utc_now
from squiggy.models.base import Base
from squiggy.models.whiteboard_user import whiteboard_user_table


class Whiteboard(Base):
    __tablename__ = 'whiteboards'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    course_id = db.Column(db.Integer, nullable=False)
    deleted_at = db.Column(db.DateTime)
    image_url = db.Column(db.Text)
    thumbnail_url = db.Column(db.Text)
    title = db.Column(db.String(255), nullable=False)
    users = db.relationship(
        'User',
        back_populates='whiteboards',
        secondary=whiteboard_user_table,
    )

    def __init__(
        self,
        course_id,
        users,
        image_url=None,
        thumbnail_url=None,
        title=None,
        whiteboard_elements=None,
    ):
        self.course_id = course_id
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.title = title
        self.users = users or []
        self.whiteboard_elements = whiteboard_elements or []

    def __repr__(self):
        return f"""<Whiteboard
            id={self.id},
            course_id={self.course_id},
            created_at={self.created_at},
            deleted_at={self.deleted_at}>
            image_url={self.image_url},
            thumbnail_url={self.thumbnail_url},
            title={self.title},
            updated_at={self.updated_at}>,
            users={self.users},
        """

    @classmethod
    def find_by_id(cls, whiteboard_id):
        return cls.query.filter_by(id=whiteboard_id, deleted_at=None).first()

    @classmethod
    def create(
        cls,
        course_id,
        title,
        users,
        image_url=None,
    ):
        whiteboard = cls(
            course_id=course_id,
            image_url=image_url,
            title=title,
            users=users,
        )
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    @classmethod
    def delete(cls, whiteboard_id):
        whiteboard = cls.find_by_id(whiteboard_id)
        if whiteboard:
            whiteboard.deleted_at = utc_now()
            std_commit()

    @classmethod
    def get_whiteboards(
            cls,
            current_user,
            limit,
            offset,
            order_by,
    ):
        order_by_clause = {
            'recent': 'w.id DESC',
        }.get(order_by)

        sql = f"""
            SELECT * FROM whiteboards w
            LEFT JOIN whiteboard_users wu ON w.id = wu.whiteboard_id
            LEFT JOIN users u ON wu.user_id = u.id
            LEFT JOIN activities act ON
                act.object_type = 'whiteboard'
                AND w.id = act.object_id
                AND act.course_id = :course_id
                AND act.user_id = :user_id
            WHERE
                w.deleted_at IS NULL
                AND w.course_id = :course_id
            ORDER BY {order_by_clause}
            LIMIT :limit OFFSET :offset
        """
        params = {
            'course_id': current_user.course.id,
            'user_id': current_user.user_id,
            'offset': offset,
            'limit': limit,
        }
        results = [db_row_to_dict(row) for row in list(db.session.execute(sql, params))]
        return {
            'offset': offset,
            'total': len(results),
            'results': results,
        }

    @classmethod
    def update(cls, whiteboard_id, title):
        whiteboard = cls.find_by_id(whiteboard_id)
        whiteboard.title = title
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    def to_api_json(self):
        def _whiteboard_element_to_json(e):
            return {
                'element': e.element,
                'uid': e.uid,
                'assetId': e.asset_id,
            }
        return {
            'id': self.id,
            'courseId': self.course_id,
            'imageUrl': self.image_url,
            'thumbnailUrl': self.thumbnail_url,
            'title': self.title,
            'users': [u.to_api_json() for u in self.users],
            'whiteboardElements': [_whiteboard_element_to_json(e) for e in self.whiteboard_elements],
            'createdAt': isoformat(self.created_at),
            'deletedAt': isoformat(self.deleted_at),
            'updatedAt': isoformat(self.updated_at),
        }
