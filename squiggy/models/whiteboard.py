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

import re
from uuid import uuid4

from squiggy import db, std_commit
from squiggy.lib.aws import get_s3_signed_url, is_s3_preview_url
from squiggy.lib.util import is_admin, is_observer, is_student, is_teaching, isoformat, utc_now
from squiggy.models.activity import Activity
from squiggy.models.asset import Asset
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.base import Base
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession
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
    def find_by_id(cls, whiteboard_id, current_user=None, include_deleted=True):
        whiteboards = cls.get_whiteboards(
            current_user=current_user,
            include_deleted=include_deleted,
            whiteboard_id=whiteboard_id,
        )
        whiteboard = whiteboards['results'][0] if whiteboards['total'] else None
        if whiteboard:
            whiteboard['whiteboardElements'] = [e.to_api_json() for e in WhiteboardElement.find_by_whiteboard_id(whiteboard_id)]
        return whiteboard

    @classmethod
    def create(
        cls,
        course_id,
        title,
        users,
    ):
        whiteboard = cls(
            course_id=course_id,
            title=title,
            users=users,
        )
        db.session.add(whiteboard)
        std_commit()
        return whiteboard.to_api_json()

    @classmethod
    def delete(cls, whiteboard_id):
        whiteboard = cls.query.filter_by(id=whiteboard_id, deleted_at=None).first()
        if whiteboard:
            whiteboard.deleted_at = utc_now()
            std_commit()

    @classmethod
    def get_exportability_summary(cls, current_user, whiteboard_id):
        summary = {
            'errored': [],
            'exportable': [],
            'pending': [],
            'updated': [],
        }
        asset_ids = []
        whiteboard_elements = WhiteboardElement.find_by_whiteboard_id(whiteboard_id=whiteboard_id)
        for whiteboard_element in whiteboard_elements:
            if not whiteboard_element.asset_id:
                element = whiteboard_element.element
                src = element.get('src')
                if src and is_s3_preview_url(src):
                    element['src'] = get_s3_signed_url(src)
                summary['exportable'].append(element)
            elif whiteboard_element.asset_id not in asset_ids:
                asset_ids.append(whiteboard_element.asset_id)

        if asset_ids:
            assets = Asset.get_assets(
                filters={'asset_ids': asset_ids},
                limit=100000,
                offset=0,
                order_by='id',
                session=current_user,
            )
            assets_by_id = dict((asset['id'], asset) for asset in assets['results'])
            for whiteboard_element in [e for e in whiteboard_elements if e.asset_id]:
                asset_id = whiteboard_element.asset_id
                asset = assets_by_id.get(asset_id)
                if asset:
                    image_url = asset['imageUrl']
                    preview_status = asset['previewStatus']
                    if not image_url or preview_status != 'done':
                        key = 'pending' if preview_status == 'pending' else 'errored'
                        summary[key].append(whiteboard_element.id)
                    else:
                        element = whiteboard_element.element
                        summary['exportable'].append(element)
                        if image_url != element.get('src'):
                            # Update preview image. Front-end will re-render the element.
                            element['src'] = image_url
                            whiteboard_element = WhiteboardElement.update(
                                asset_id=asset_id,
                                element=element,
                                uuid=whiteboard_element.uuid,
                                whiteboard_id=whiteboard_id,
                            )
                            summary['updated'].append(whiteboard_element.to_api_json())
                else:
                    summary['errored'] = f'Asset (id: {asset_id}) not found for whiteboard element.'
        return summary

    @classmethod
    def get_whiteboards(
            cls,
            course_id=None,
            current_user=None,
            include_deleted=False,
            keywords=None,
            limit=20,
            offset=0,
            order_by='recent',
            user_id=None,
            whiteboard_id=None,
    ):
        params = {
            'course_id': course_id,
            'current_user_id': current_user.user_id if current_user else None,
            'keywords': ('%' + re.sub(r'\s+', '%', keywords.strip()) + '%') if keywords else None,
            'limit': limit,
            'offset': offset,
            'user_id': user_id,
            'whiteboard_id': whiteboard_id,
        }
        # Construct fragments of SQL
        where_clause = _get_whiteboards_where_clause(
            course_id=course_id,
            current_user=current_user,
            include_deleted=include_deleted,
            keywords=keywords,
            params=params,
            user_id=user_id,
            whiteboard_id=whiteboard_id,
        )
        join_clause = """
            LEFT JOIN whiteboard_users wu ON wu.whiteboard_id = w.id
            LEFT JOIN whiteboard_sessions s ON s.user_id = wu.user_id
            LEFT JOIN users u ON wu.user_id = u.id AND u.canvas_enrollment_state != 'inactive'
            LEFT JOIN activities act ON act.object_type = 'whiteboard' AND w.id = act.object_id
        """
        default_order_by = 'w.id DESC'
        order_by_clause = {
            'collaborator': 'u.canvas_full_name, u.canvas_user_id',
            'recent': default_order_by,
        }.get(order_by) or default_order_by

        # First, get whiteboard_ids
        sql = f'SELECT w.id FROM whiteboards w {join_clause} {where_clause}'
        all_whiteboard_ids = list({row['id'] for row in list(db.session.execute(sql, params))})
        params['whiteboard_ids'] = all_whiteboard_ids

        # Next, get search results per whiteboard_ids above.
        sql = f"""
            SELECT w.*, u.canvas_course_role, u.canvas_course_sections, u.canvas_enrollment_state, u.canvas_full_name,
              u.canvas_image, u.canvas_user_id, u.id AS user_id, s.socket_id
            FROM whiteboards w
            {join_clause}
            WHERE w.id = ANY(:whiteboard_ids)
            ORDER BY {order_by_clause}, u.canvas_full_name
            LIMIT :limit OFFSET :offset
        """
        whiteboards_by_id = {}
        users_by_whiteboard_id = {}
        rows = list(db.session.execute(sql, params))

        # Delete stale sessions
        WhiteboardSession.delete_stale_sessions([row['id'] for row in rows])

        for row in rows:
            whiteboard_id = int(row['id'])
            deleted_at = row['deleted_at']
            whiteboard = whiteboards_by_id.get(whiteboard_id) or {
                'id': whiteboard_id,
                'courseId': row['course_id'],
                'createdAt': isoformat(row['created_at']),
                'deletedAt': isoformat(deleted_at),
                'imageUrl': row['image_url'],
                'isReadOnly': deleted_at is not None,
                'thumbnailUrl': row['thumbnail_url'],
                'title': row['title'],
                'updatedAt': isoformat(row['updated_at']),
                'users': [],
            }
            whiteboards_by_id[whiteboard_id] = whiteboard
            user_id = row['user_id']
            if user_id:
                if whiteboard_id not in users_by_whiteboard_id:
                    users_by_whiteboard_id[whiteboard_id] = {}
                users_by_whiteboard_id[whiteboard_id][user_id] = {
                    'id': user_id,
                    'canvasCourseRole': row['canvas_course_role'],
                    'canvasCourseSections': row['canvas_course_sections'],
                    'canvasEnrollmentState': row['canvas_enrollment_state'],
                    'canvasFullName': row['canvas_full_name'],
                    'canvasImage': row['canvas_image'],
                    'canvasUserId': row['canvas_user_id'],
                    'isAdmin': is_admin(row),
                    'isObserver': is_observer(row),
                    'isOnline': bool(row['socket_id']),
                    'isStudent': is_student(row),
                    'isTeaching': is_teaching(row),
                }

        for whiteboard_id, users_by_id in users_by_whiteboard_id.items():
            whiteboard = whiteboards_by_id[whiteboard_id]
            whiteboard['users'] = list(users_by_id.values())
            whiteboard['onlineCount'] = len([u for u in whiteboard['users'] if u['isOnline']])
        return {
            'offset': offset,
            'results': list(whiteboards_by_id.values()),
            'total': len(all_whiteboard_ids),
        }

    @classmethod
    def remix(cls, asset, course_id, user):
        whiteboard = cls.create(
            course_id=course_id,
            title=asset.title,
            users=[user],
        )
        whiteboard_id = whiteboard['id']
        for a in AssetWhiteboardElement.find_by_asset_id(asset.id):
            WhiteboardElement.create(
                asset_id=a.element_asset_id,
                element=a.element,
                uuid=str(uuid4()),
                whiteboard_id=whiteboard_id,
            )
        # If user is remixing their own whiteboard then no 'activity' is created.
        user_id = user.id
        course_id = user.course.id
        if user_id not in [user.id for user in asset.users]:
            Activity.create(
                activity_type='whiteboard_remix',
                course_id=course_id,
                user_id=user_id,
                object_type='asset',
                object_id=asset.id,
                asset_id=asset.id,
            )
            for asset_user in asset.users:
                Activity.create(
                    activity_type='get_whiteboard_remix',
                    course_id=course_id,
                    user_id=asset_user.id,
                    object_type='asset',
                    object_id=asset.id,
                    asset_id=asset.id,
                )
        return whiteboard

    @classmethod
    def restore(cls, whiteboard_id):
        whiteboard = cls.query.filter_by(id=whiteboard_id).first()
        if whiteboard and whiteboard.deleted_at:
            whiteboard.deleted_at = None
            whiteboard.updated_at = utc_now()
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
    def update(cls, title, users, whiteboard_id):
        whiteboard = cls.query.filter_by(id=whiteboard_id).first()
        whiteboard.title = title
        whiteboard.users = users
        db.session.add(whiteboard)
        std_commit()
        return whiteboard

    @classmethod
    def update_preview(cls, image_url, thumbnail_url, whiteboard_id):
        whiteboard = cls.query.filter_by(id=whiteboard_id).first()
        if thumbnail_url:
            whiteboard.thumbnail_url = thumbnail_url
        if image_url:
            whiteboard.image_url = image_url
        db.session.add(whiteboard)
        std_commit()
        return True

    def to_api_json(self):
        user_ids_online = [session.user_id for session in WhiteboardSession.find(self.id)]

        def _user_api_json(user):
            return {
                **user.to_api_json(),
                'isOnline': user.id in user_ids_online,
            }

        return {
            'id': self.id,
            'courseId': self.course_id,
            'imageUrl': self.image_url,
            'isReadOnly': self.deleted_at is not None,
            'thumbnailUrl': self.thumbnail_url,
            'title': self.title,
            'users': [_user_api_json(user) for user in self.users if user.canvas_enrollment_state != 'inactive'],
            'whiteboardElements': [e.to_api_json() for e in WhiteboardElement.find_by_whiteboard_id(self.id)],
            'createdAt': isoformat(self.created_at),
            'deletedAt': isoformat(self.deleted_at),
            'updatedAt': isoformat(self.updated_at),
        }


def _get_whiteboards_where_clause(
        params,
        course_id=None,
        current_user=None,
        include_deleted=False,
        keywords=None,
        user_id=None,
        whiteboard_id=None,
):
    where_clause = 'WHERE TRUE'
    if course_id:
        where_clause += ' AND w.course_id = :course_id'
    if not include_deleted:
        where_clause += ' AND w.deleted_at IS NULL'
    if keywords:
        where_clause += ' AND (w.title ILIKE :keywords)'
    if user_id:
        where_clause += ' AND u.id = :user_id'
    if whiteboard_id:
        where_clause += ' AND w.id = :whiteboard_id'
    if current_user:
        if current_user.is_student or current_user.is_observer:
            sql = 'SELECT whiteboard_id FROM whiteboard_users WHERE user_id = :current_user_id'
            params['my_whiteboard_ids'] = [row['whiteboard_id'] for row in list(db.session.execute(sql, params))]
            where_clause += ' AND w.id = ANY(:my_whiteboard_ids)'
    return where_clause
