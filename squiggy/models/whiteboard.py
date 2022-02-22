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
from squiggy.lib.util import isoformat, utc_now
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.base import Base
from squiggy.models.whiteboard_element import WhiteboardElement
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
    ):
        self.course_id = course_id
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.title = title
        self.users = users or []

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
    def find_by_id(cls, whiteboard_id, include_deleted=True):
        whiteboards = cls.get_whiteboards(include_deleted=include_deleted, whiteboard_id=whiteboard_id)
        return whiteboards['results'][0] if whiteboards['total'] else None

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
        whiteboard = cls.query.filter_by(id=whiteboard_id, deleted_at=None).first()
        if whiteboard:
            whiteboard.deleted_at = utc_now()
            std_commit()

    @classmethod
    def get_whiteboards(
            cls,
            course_id=None,
            include_deleted=False,
            limit=20,
            offset=0,
            order_by='recent',
            whiteboard_id=None,
    ):
        order_by_clause = {
            'recent': 'w.id DESC',
        }.get(order_by)

        sql = f"""
            SELECT
                w.*, u.canvas_course_role, u.canvas_course_sections, u.canvas_enrollment_state, u.canvas_full_name,
                u.canvas_image, u.canvas_user_id, u.id AS user_id
            FROM whiteboards w
            LEFT JOIN whiteboard_users wu ON w.id = wu.whiteboard_id
            LEFT JOIN users u ON wu.user_id = u.id
            LEFT JOIN activities act ON
                act.object_type = 'whiteboard'
                AND w.id = act.object_id
                AND act.course_id = :course_id
            WHERE
                {'TRUE' if include_deleted else 'w.deleted_at IS NULL'}
                {'AND w.course_id = :course_id' if course_id else ''}
                {'AND w.id = :whiteboard_id' if whiteboard_id else ''}
            ORDER BY {order_by_clause}, u.canvas_full_name
            LIMIT :limit OFFSET :offset
        """
        params = {
            'course_id': course_id,
            'offset': offset,
            'limit': limit,
            'whiteboard_id': whiteboard_id,
        }
        whiteboards_by_id = {}
        for row in list(db.session.execute(sql, params)):
            whiteboard_id = row['id']
            whiteboard = whiteboards_by_id.get(whiteboard_id) or {
                'id': whiteboard_id,
                'courseId': row['course_id'],
                'createdAt': isoformat(row['created_at']),
                'deletedAt': isoformat(row['deleted_at']),
                'imageUrl': row['image_url'],
                'thumbnailUrl': row['thumbnail_url'],
                'title': row['title'],
                'updatedAt': isoformat(row['updated_at']),
                'sessions': [],
                'users': [],
            }
            user_id = row['user_id']
            if user_id:
                whiteboard['users'].append({
                    'id': user_id,
                    'canvasCourseRole': row['canvas_course_role'],
                    'canvasCourseSections': row['canvas_course_sections'],
                    'canvasEnrollmentState': row['canvas_enrollment_state'],
                    'canvasFullName': row['canvas_full_name'],
                    'canvasImage': row['canvas_image'],
                    'canvasUserId': row['canvas_user_id'],
                })
            whiteboards_by_id[whiteboard_id] = whiteboard
        # Get sessions
        sql = 'SELECT * FROM whiteboard_sessions WHERE whiteboard_id = ANY(:whiteboard_ids) ORDER BY created_at'
        for row in db.session.execute(sql, {'whiteboard_ids': list(whiteboards_by_id.keys())}):
            whiteboard_id = row['whiteboard_id']
            whiteboards_by_id[whiteboard_id]['sessions'].append({
                'createdAt': isoformat(row['created_at']),
                'socketId': row['socket_id'],
                'updatedAt': isoformat(row['updated_at']),
                'userId': row['user_id'],
            })
        return {
            'offset': offset,
            'results': list(whiteboards_by_id.values()),
            'total': len(whiteboards_by_id),
        }

    @classmethod
    def reconstitute(cls, asset, course_id):
        # Remix
        whiteboard = cls.create(
            course_id=course_id,
            image_url=asset.image_url,
            title=asset.title,
        )
        for asset_whiteboard_element in AssetWhiteboardElement.find_by_asset_id(asset.id):
            WhiteboardElement.create(
                asset_id=asset.id,
                element=asset_whiteboard_element.element,  # TODO: Storage.signWhiteboardElementSrc(asset_whiteboard_element.element)
                uid=whiteboard.uid,
                whiteboard_id=whiteboard.id,
            )
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    @classmethod
    def undelete(cls, whiteboard_id, title):
        whiteboard = cls.find_by_id(whiteboard_id)
        whiteboard.title = title
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    @classmethod
    def update(cls, whiteboard_id, title):
        whiteboard = cls.find_by_id(whiteboard_id)
        whiteboard.title = title
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    def to_api_json(self):
        return {
            'id': self.id,
            'courseId': self.course_id,
            'imageUrl': self.image_url,
            'thumbnailUrl': self.thumbnail_url,
            'title': self.title,
            'users': [u.to_api_json() for u in self.users],
            'whiteboardElements': [e.to_api_json() for e in WhiteboardElement.find_by_whiteboard_id(self.id)],
            'createdAt': isoformat(self.created_at),
            'deletedAt': isoformat(self.deleted_at),
            'updatedAt': isoformat(self.updated_at),
        }
