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

from itertools import groupby
import re

from sqlalchemy.dialects.postgresql import ENUM, JSON
from sqlalchemy.sql import text
from squiggy import db, std_commit
from squiggy.lib.aws import get_s3_signed_url, is_s3_preview_url
from squiggy.lib.util import camelize, isoformat, utc_now
from squiggy.models.activity import Activity
from squiggy.models.asset_category import asset_category_table
from squiggy.models.asset_user import asset_user_table
from squiggy.models.base import Base
from squiggy.models.user import User

assets_sort_by_options = {
    'recent': 'Most recent',
    'likes': 'Most likes',
    'views': 'Most views',
    'comments': 'Most comments',
}

assets_type = ENUM(
    'file',
    'link',
    'thought',
    name='enum_assets_type',
    create_type=False,
)


class Asset(Base):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    asset_type = db.Column('type', assets_type, nullable=False)
    body = db.Column(db.Text)
    canvas_assignment_id = db.Column(db.Integer)
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    course_id = db.Column(db.Integer, nullable=False)
    deleted_at = db.Column(db.DateTime)
    description = db.Column(db.Text)
    dislikes = db.Column(db.Integer, nullable=False, default=0)
    download_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    likes = db.Column(db.Integer, nullable=False, default=0)
    mime = db.Column(db.String(255))
    pdf_url = db.Column(db.String(255))
    preview_metadata = db.Column(JSON)
    preview_status = db.Column(db.String(255), nullable=False, default='pending')
    source = db.Column(db.String(255))
    title = db.Column(db.String(255))
    url = db.Column(db.String(255))
    views = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.Boolean, nullable=False, default=True)
    categories = db.relationship(
        'Category',
        secondary=asset_category_table,
        backref='assets',
    )
    users = db.relationship(
        User.__name__,
        secondary=asset_user_table,
        backref='assets',
    )

    def __init__(
        self,
        asset_type,
        course_id,
        categories=None,
        description=None,
        download_url=None,
        mime=None,
        source=None,
        title=None,
        url=None,
        users=None,
        visible=True,
    ):
        self.asset_type = asset_type
        self.categories = categories or []
        self.course_id = course_id
        self.description = description
        self.download_url = download_url
        self.mime = mime
        self.source = source
        self.title = title
        self.url = url
        self.users = users or []
        self.visible = visible

    def __repr__(self):
        return f"""<Asset
                    asset_type={self.asset_type},
                    categories={self.categories},
                    users={self.users},
                    course_id={self.course_id},
                    description={self.description},
                    source={self.source},
                    title={self.title},
                    url={self.url},
                    visible={self.visible},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    @classmethod
    def find_by_id(cls, asset_id):
        return cls.query.filter_by(id=asset_id, deleted_at=None).first()

    @classmethod
    def create(
            cls,
            asset_type,
            course_id,
            title,
            users,
            categories=None,
            description=None,
            download_url=None,
            mime=None,
            source=None,
            url=None,
            visible=True,
    ):
        asset = cls(
            asset_type=asset_type,
            categories=categories,
            course_id=course_id,
            description=description,
            download_url=download_url,
            source=source,
            title=title,
            url=url,
            users=users,
            visible=visible,
        )
        db.session.add(asset)
        std_commit()

        # Invisible assets generate no activities.
        if visible:
            for user in users:
                Activity.create(
                    activity_type='asset_add',
                    course_id=course_id,
                    user_id=user.id,
                    object_type='asset',
                    object_id=asset.id,
                    asset_id=asset.id,
                )

        return asset

    @classmethod
    def delete(cls, asset_id):
        asset = cls.find_by_id(asset_id)
        if asset:
            asset.deleted_at = utc_now()
            std_commit()

    @classmethod
    def update(
            cls,
            asset_id,
            title,
            categories=None,
            description=None,
    ):
        asset = Asset.find_by_id(asset_id)
        asset.title = title
        asset.description = description
        asset.categories = categories
        db.session.add(asset)
        std_commit()
        return asset

    @classmethod
    def get_assets(cls, session, sort, offset, limit, filters):
        params = {
            'course_id': session.course.id,
            'user_id': session.user.id,
            'asset_types': filters.get('asset_type'),
            'category_id': filters.get('category_id'),
            'owner_id': filters.get('owner_id'),
            'section_id': filters.get('section_id'),
            'offset': offset,
            'limit': limit,
        }

        from_clause = """FROM assets a
            LEFT JOIN asset_categories ac ON a.id = ac.asset_id
            LEFT JOIN categories c ON c.id = ac.category_id
            LEFT JOIN asset_users au ON a.id = au.asset_id
            LEFT JOIN users u ON au.user_id = u.id
            LEFT JOIN activities act ON a.id = act.asset_id
                AND act.course_id = :course_id
                AND act.user_id = :user_id
                AND act.object_type = 'asset'
                AND act.type = 'asset_like'"""

        where_clause = _build_where_clause(filters, params)
        order_clause = _build_order_clause(sort)

        assets_query = text(f"""SELECT DISTINCT ON (a.id, a.likes, a.views, a.comment_count) a.*, act.type AS activity_type
            {from_clause} {where_clause} {order_clause}
            LIMIT :limit OFFSET :offset""")
        assets_result = list(db.session.execute(assets_query, params))

        count_query = text(f'SELECT COUNT(DISTINCT(a.id))::int AS count {from_clause} {where_clause}')
        count_result = db.session.execute(count_query, params).fetchone()
        total = (count_result and count_result[0]) or 0

        asset_ids = [r['id'] for r in assets_result]

        users_query = text("""SELECT au.asset_id,
            u.id, u.canvas_user_id, u.canvas_course_role, u.canvas_course_sections, u.canvas_enrollment_state, u.canvas_full_name, u.canvas_image
            FROM users u JOIN asset_users au
            ON au.user_id = u.id AND au.asset_id = ANY(:asset_ids)
            ORDER BY au.asset_id""")
        users_result = db.session.execute(users_query, {'asset_ids': asset_ids})

        def _row_to_json_obj(row):
            d = dict(row)
            json_obj = dict()
            for key in d.keys():
                if key.endswith('_at'):
                    json_obj[camelize(key)] = isoformat(d[key])
                elif isinstance(d[key], dict):
                    json_obj[camelize(key)] = _row_to_json_obj(d[key])
                else:
                    json_obj[camelize(key)] = d[key]
            return json_obj

        users_by_asset = dict()
        for asset_id, user_rows in groupby(users_result, lambda r: r['asset_id']):
            users_by_asset[asset_id] = [_row_to_json_obj(r) for r in user_rows]

        def _row_to_json_asset(row):
            json_asset = _row_to_json_obj(row)

            # Has the current user liked the asset?
            json_asset['liked'] = (json_asset['activityType'] == 'asset_like')

            if json_asset['id'] in users_by_asset:
                json_asset['users'] = users_by_asset[json_asset['id']]

            if is_s3_preview_url(json_asset['imageUrl']):
                json_asset['imageUrl'] = get_s3_signed_url(json_asset['imageUrl'])
            if is_s3_preview_url(json_asset['thumbnailUrl']):
                json_asset['thumbnailUrl'] = get_s3_signed_url(json_asset['thumbnailUrl'])

            return json_asset

        results = {
            'offset': offset,
            'total': total,
            'results': [_row_to_json_asset(r) for r in assets_result],
        }

        return results

    def to_api_json(self):
        return {
            'id': self.id,
            'assetType': self.asset_type,
            'body': self.body,
            'canvasAssignment_id': self.canvas_assignment_id,
            'categories': [c.to_api_json() for c in self.categories],
            'commentCount': self.comment_count,
            'courseId': self.course_id,
            'description': self.description,
            'dislikes': self.dislikes,
            'downloadUrl': self.download_url,
            'imageUrl': self.image_url,
            'likes': self.likes,
            'mime': self.mime,
            'pdfUrl': self.pdf_url,
            'previewMetadata': self.preview_metadata,
            'previewStatus': self.preview_status,
            'source': self.source,
            'title': self.title,
            'url': self.url,
            'users': [u.to_api_json() for u in self.users],
            'views': self.views,
            'visible': self.visible,
            'createdAt': isoformat(self.created_at),
            'deletedAt': isoformat(self.deleted_at),
            'updatedAt': isoformat(self.updated_at),
        }


def _build_order_clause(sort):
    if (sort == 'recent'):
        return ' ORDER BY a.id DESC'
    elif (sort == 'likes'):
        return ' ORDER BY a.likes DESC, a.id DESC'
    elif (sort == 'views'):
        return ' ORDER BY a.views DESC, a.id DESC'
    elif (sort == 'comments'):
        return ' ORDER BY a.comment_count DESC, a.id DESC'
    else:
        return ' ORDER BY a.id DESC'


def _build_where_clause(filters, params):
    where_clause = """WHERE
        a.deleted_at IS NULL
        AND a.course_id = :course_id
        AND a.visible = TRUE
        AND (c.visible = TRUE OR c.visible IS NULL)"""

    if filters.get('keywords'):
        where_clause += ' AND (a.title ILIKE :keywords OR a.description ILIKE :keywords)'
        params['keywords'] = '%' + re.sub(r'\s+', '%', filters['keywords'].strip()) + '%'

    if filters.get('asset_type'):
        where_clause += ' AND a.type IN(:asset_types)'

    if filters.get('category_id'):
        where_clause += ' AND c.id = :category_id'

    if filters.get('owner_id'):
        where_clause += ' AND au.user_id = :owner_id'

    if filters.get('section_id'):
        where_clause += ' AND (array_position(u.canvas_course_sections, :section_id) > 0)'

    if filters.get('has_comments') is not None:
        where_clause += (' AND a.comment_count > 0' if filters['has_comments'] else ' AND a.comment_count = 0')

    if filters.get('has_likes') is not None:
        where_clause += (' AND a.likes > 0' if filters['has_likes'] else ' AND a.likes = 0')

    if filters.get('has_views') is not None:
        where_clause += (' AND a.views > 0' if filters['has_views'] else ' AND a.views = 0')

    return where_clause
