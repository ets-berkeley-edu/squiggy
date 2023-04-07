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

from itertools import groupby
import re
from urllib.parse import urlparse

from sqlalchemy.dialects.postgresql import ENUM, JSON
from sqlalchemy.sql import text
from squiggy import db, std_commit
from squiggy.lib.aws import get_s3_signed_url
from squiggy.lib.http import request
from squiggy.lib.previews import generate_previews
from squiggy.lib.util import db_row_to_dict, isoformat, utc_now
from squiggy.models.activity import Activity
from squiggy.models.asset_category import asset_category_table
from squiggy.models.asset_whiteboard_element import AssetWhiteboardElement
from squiggy.models.base import Base

assets_sort_by_options = {
    'recent': 'Most recent',
    'likes': 'Most likes',
    'views': 'Most views',
    'comments': 'Most comments',
}

assets_type = ENUM(
    'file',
    'link',
    'whiteboard',
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
    created_by = db.Column(db.Integer, nullable=False)
    deleted_at = db.Column(db.DateTime)
    description = db.Column(db.Text)
    dislikes = db.Column(db.Integer, nullable=False, default=0)
    download_url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    likes = db.Column(db.Integer, nullable=False, default=0)
    mime = db.Column(db.String(255))
    pdf_url = db.Column(db.Text)
    preview_metadata = db.Column(JSON)
    preview_status = db.Column(db.String(255), nullable=False, default='pending')
    source = db.Column(db.String(255))
    thumbnail_url = db.Column(db.Text)
    title = db.Column(db.String(255))
    url = db.Column(db.Text)
    views = db.Column(db.Integer, nullable=False, default=0)
    visible = db.Column(db.Boolean, nullable=False, default=True)
    categories = db.relationship(
        'Category',
        secondary=asset_category_table,
        backref='assets',
    )

    comments = db.relationship('Comment', back_populates='asset', cascade='all, delete-orphan')

    def __init__(
        self,
        asset_type,
        course_id,
        created_by,
        canvas_assignment_id=None,
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
        self.canvas_assignment_id = canvas_assignment_id
        self.categories = categories or []
        self.course_id = course_id
        self.created_by = created_by
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
                    canvas_assignment_id={self.canvas_assignment_id},
                    description={self.description},
                    source={self.source},
                    title={self.title},
                    url={self.url},
                    visible={self.visible},
                    created_at={self.created_at},
                    created_by={self.created_by},
                    updated_at={self.updated_at},
                    deleted_at={self.deleted_at}>
                """

    @classmethod
    def find_by_id(cls, asset_id):
        return cls.query.filter_by(id=asset_id, deleted_at=None).first()

    @classmethod
    def create(
        cls,
        asset_type,
        course_id,
        created_by,
        title,
        users,
        canvas_assignment_id=None,
        categories=None,
        description=None,
        download_url=None,
        mime=None,
        source=None,
        url=None,
        visible=True,
        create_activity=True,
    ):
        asset = cls(
            asset_type=asset_type,
            canvas_assignment_id=canvas_assignment_id,
            categories=categories,
            course_id=course_id,
            created_by=created_by,
            description=description,
            download_url=download_url,
            mime=mime,
            source=source,
            title=title,
            url=url,
            users=users,
            visible=visible,
        )
        db.session.add(asset)
        std_commit()

        preview_url = download_url if asset_type in ['file', 'whiteboard'] else url
        _generate_previews(asset, preview_url)

        # Invisible assets generate no activities.
        if visible and create_activity is not False:
            for user in users:
                activity_type = 'whiteboard_export' if asset_type == 'whiteboard' else 'asset_add'
                Activity.create(
                    activity_type=activity_type,
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
        asset.categories = categories or []
        db.session.add(asset)
        std_commit()
        return asset

    @classmethod
    def get_assets(cls, current_user, filters, offset, order_by, limit, include_hidden=False):
        params = {
            'asset_ids': filters.get('asset_ids'),
            'asset_types': filters.get('asset_type'),
            'category_id': filters.get('category_id'),
            'course_id': current_user.course_id,
            'group_id': filters.get('group_id'),
            'limit': limit,
            'my_asset_ids': current_user.asset_ids,
            'offset': offset,
            'owner_id': filters.get('owner_id'),
            'section': filters.get('section'),
            'user_id': current_user.id,
        }

        from_clause = _build_from_clause(filters=filters, current_user=current_user)
        where_clause = _build_where_clause(
            filters=filters,
            include_hidden=include_hidden,
            params=params,
            current_user=current_user,
        )
        order_clause = _build_order_clause(order_by)

        assets_query = text(f"""SELECT DISTINCT ON (a.id, a.likes, a.views, a.comment_count) a.*, act.type AS activity_type
            {from_clause} {where_clause} {order_clause}
            LIMIT :limit OFFSET :offset""")
        assets_result = list(db.session.execute(assets_query, params))

        count_query = text(f'SELECT COUNT(DISTINCT(a.id))::int AS count {from_clause} {where_clause}')
        count_result = db.session.execute(count_query, params).fetchone()
        total = (count_result and count_result[0]) or 0

        asset_ids = [r['id'] for r in assets_result]

        users_query = text("""
            SELECT
                au.asset_id, u.id, u.canvas_user_id, u.canvas_course_role, u.canvas_course_sections,
                u.canvas_enrollment_state, u.canvas_full_name, u.canvas_image
            FROM users u JOIN asset_users au
            ON au.user_id = u.id AND au.asset_id = ANY(:asset_ids)
            ORDER BY au.asset_id
        """)
        users_result = db.session.execute(users_query, {'asset_ids': asset_ids})
        users_by_asset = dict()
        for asset_id, user_rows in groupby(users_result, lambda r: r['asset_id']):
            users_by_asset[asset_id] = [db_row_to_dict(r) for r in user_rows]

        def _row_to_json_asset(row):
            json_asset = db_row_to_dict(row)

            # Has the user liked the asset?
            json_asset['liked'] = (json_asset['activityType'] == 'asset_like')

            if json_asset['id'] in users_by_asset:
                json_asset['users'] = users_by_asset[json_asset['id']]
            json_asset['thumbnailUrl'] = get_s3_signed_url(json_asset['thumbnailUrl'])

            return json_asset

        results = {
            'offset': offset,
            'total': total,
            'results': [_row_to_json_asset(r) for r in assets_result],
        }

        return results

    def get_used_in_assets(self):
        def _to_api_json(row):
            return {
                'id': row['id'],
                'description': row['description'],
                'title': row['title'],
                'visible': row['visible'],
            }
        sql = text("""SELECT DISTINCT a.id, a.title, a.description, a.visible
            FROM assets a
            JOIN asset_whiteboard_elements e ON a.id = e.asset_id
            WHERE e.element_asset_id = :element_asset_id AND a.deleted_at IS NULL
        """)
        return [_to_api_json(row) for row in db.session.execute(sql, {'element_asset_id': self.id})]

    def is_used_in_whiteboards(self):
        sql = text("""SELECT COUNT(DISTINCT w.id)
            FROM whiteboards w
            JOIN whiteboard_elements we ON w.id = we.whiteboard_id
            WHERE we.asset_id = :asset_id AND w.deleted_at IS NULL
        """)
        count = db.session.execute(sql, {'asset_id': self.id}).first()[0]
        return count > 0

    def add_like(self, user_id):
        like_activity = Activity.create_unless_exists(
            activity_type='asset_like',
            course_id=self.course_id,
            user_id=user_id,
            object_type='asset',
            object_id=self.id,
            asset_id=self.id,
        )
        if like_activity:
            for asset_owner in self.users:
                Activity.create_unless_exists(
                    activity_type='get_asset_like',
                    course_id=self.course_id,
                    user_id=asset_owner.id,
                    object_type='asset',
                    object_id=self.id,
                    asset_id=self.id,
                    actor_id=user_id,
                    reciprocal_id=like_activity.id,
                )
        self.likes = Activity.query.filter_by(asset_id=self.id, activity_type='asset_like').count()
        db.session.add(self)
        std_commit()
        return True

    def remove_like(self, user_id):
        db.session.query(Activity).filter_by(
            object_id=self.id,
            object_type='asset',
            activity_type='asset_like',
            user_id=user_id,
        ).delete()
        db.session.query(Activity).filter_by(
            object_id=self.id,
            object_type='asset',
            activity_type='get_asset_like',
            actor_id=user_id,
        ).delete()
        std_commit()
        Activity.recalculate_points(course_id=self.course_id, user_ids=[user_id] + [u.id for u in self.users])
        self.likes = Activity.query.filter_by(object_id=self.id, object_type='asset', activity_type='asset_like').count()
        db.session.add(self)
        std_commit()
        return True

    def increment_views(self, user_id):
        view_activity = Activity.create(
            activity_type='asset_view',
            course_id=self.course_id,
            user_id=user_id,
            object_type='asset',
            object_id=self.id,
            asset_id=self.id,
        )
        if view_activity:
            for asset_owner in self.users:
                Activity.create(
                    activity_type='get_asset_view',
                    course_id=self.course_id,
                    user_id=asset_owner.id,
                    object_type='asset',
                    object_id=self.id,
                    asset_id=self.id,
                    actor_id=user_id,
                    reciprocal_id=view_activity.id,
                )
        self.views = Activity.query.filter_by(asset_id=self.id, activity_type='asset_view').count()
        db.session.add(self)
        std_commit()
        return True

    def refresh_comments_count(self):
        self.comment_count = len(self.comments)
        db.session.add(self)
        std_commit()
        return self.comment_count

    def refresh_asset_preview_image(self):
        self.update_preview(preview_status='pending')
        preview_url = self.download_url if self.asset_type in ['file', 'whiteboard'] else self.url
        _generate_previews(
            asset=self,
            preview_url=preview_url,
        )

    def update_preview(self, **kwargs):
        if kwargs.get('preview_status'):
            self.preview_status = kwargs['preview_status']
        if kwargs.get('thumbnail_url'):
            self.thumbnail_url = kwargs['thumbnail_url']
        if kwargs.get('image_url'):
            self.image_url = kwargs['image_url']
        if kwargs.get('pdf_url'):
            self.pdf_url = kwargs['pdf_url']
        if kwargs.get('metadata'):
            self.preview_metadata = kwargs['metadata']
        db.session.add(self)
        std_commit()
        return True

    def to_api_json(self, user_id=None):
        image_url = get_s3_signed_url(self.image_url)
        pdf_url = get_s3_signed_url(self.pdf_url)
        thumbnail_url = get_s3_signed_url(self.thumbnail_url)

        liked = False
        if user_id:
            like_query = Activity.query.filter_by(
                object_id=self.id,
                object_type='asset',
                activity_type='asset_like',
                user_id=user_id,
            )
            if like_query.first() is not None:
                liked = True
        api_json = {
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
            'imageUrl': image_url,
            'isUsedInWhiteboards': self.is_used_in_whiteboards(),
            'liked': liked,
            'likes': self.likes,
            'mime': self.mime,
            'pdfUrl': pdf_url,
            'previewMetadata': self.preview_metadata,
            'previewStatus': self.preview_status,
            'source': self.source,
            'thumbnailUrl': thumbnail_url,
            'title': self.title,
            'url': self.url,
            'usedInAssets': self.get_used_in_assets(),
            'users': [u.to_api_json() for u in self.users],
            'views': self.views,
            'visible': self.visible,
            'createdAt': isoformat(self.created_at),
            'createdBy': self.created_by,
            'deletedAt': isoformat(self.deleted_at),
            'updatedAt': isoformat(self.updated_at),
        }
        if self.asset_type == 'whiteboard':
            api_json['isReadOnly'] = True
            whiteboard_elements = []
            for w in AssetWhiteboardElement.find_by_asset_id(self.id):
                element = {
                    **w.element,
                    **{
                        'uuid': w.uuid,
                    },
                }
                whiteboard_elements.append({
                    'assetId': w.element_asset_id,
                    'createdAt': isoformat(w.created_at),
                    'element': element,
                    'updatedAt': isoformat(self.updated_at),
                    'uuid': w.uuid,
                    'zIndex': w.z_index,
                })
            api_json['whiteboardElements'] = whiteboard_elements
        return api_json


def validate_asset_url(url):
    error_message = None
    # For the moment, validation is restricted to Google Jamboard URLs.
    if urlparse(url).netloc == 'jamboard.google.com':
        response = request(url)
        # Google signals restricted access not with a 403 but with a redirect to a login page.
        if response and urlparse(response.url).netloc == 'accounts.google.com' and urlparse(response.url).path == '/ServiceLogin':
            error_message = 'In order to add a Google Jamboard to the Asset Library, sharing must be set to "Anyone with the link."'
    return error_message


def _build_from_clause(filters, current_user):
    from_clause = """
        FROM assets a
            LEFT JOIN asset_categories ac ON a.id = ac.asset_id
            LEFT JOIN categories c ON c.id = ac.category_id
            LEFT JOIN asset_users au ON a.id = au.asset_id
            LEFT JOIN users u ON au.user_id = u.id
            LEFT JOIN activities act ON a.id = act.asset_id
                AND act.course_id = :course_id
                AND act.user_id = :user_id
                AND act.object_type = 'asset'
                AND act.type = 'asset_like'
    """
    if current_user.is_student and current_user.protect_assets_per_section or filters.get('group_id'):
        from_clause += """
            LEFT JOIN users asset_owner
                ON a.created_by = asset_owner.id
        """
    if filters.get('group_id'):
        from_clause += """
            JOIN course_group_memberships cgm ON
                cgm.canvas_user_id IN (u.canvas_user_id, asset_owner.canvas_user_id)
                AND cgm.course_group_id = :group_id
        """
    return from_clause


def _build_order_clause(order_by):
    if (order_by == 'recent'):
        return ' ORDER BY a.id DESC'
    elif (order_by == 'likes'):
        return ' ORDER BY a.likes DESC, a.id DESC'
    elif (order_by == 'views'):
        return ' ORDER BY a.views DESC, a.id DESC'
    elif (order_by == 'comments'):
        return ' ORDER BY a.comment_count DESC, a.id DESC'
    else:
        return ' ORDER BY a.id DESC'


def _build_where_clause(filters, include_hidden, params, current_user):
    where_clause = """WHERE
        a.deleted_at IS NULL
        AND a.course_id = :course_id
        AND (c.visible = TRUE OR c.visible IS NULL)"""

    if not include_hidden:
        where_clause += ' AND a.visible = TRUE'
    if not current_user.is_admin and not current_user.is_teaching:
        where_clause += ' AND (a.visible = TRUE OR a.id = ANY(:my_asset_ids))'
    if current_user.is_student and current_user.protect_assets_per_section:
        where_clause += """ AND (
            asset_owner.id = :user_id
            OR to_jsonb(asset_owner.canvas_course_sections) ?| :user_course_sections
            OR NOT lower(asset_owner.canvas_course_role) SIMILAR TO '%(student|learner)%'
        )"""
        params['user_course_sections'] = current_user.canvas_course_sections
    if filters.get('keywords'):
        where_clause += ' AND (a.title ILIKE :keywords OR a.description ILIKE :keywords)'
        params['keywords'] = '%' + re.sub(r'\s+', '%', filters['keywords'].strip()) + '%'

    if filters.get('asset_type'):
        where_clause += ' AND a.type IN(:asset_types)'

    if filters.get('category_id'):
        where_clause += ' AND c.id = :category_id'

    if filters.get('owner_id'):
        where_clause += ' AND au.user_id = :owner_id'

    if filters.get('section'):
        where_clause += ' AND (array_position(u.canvas_course_sections, :section) > 0)'

    return where_clause


def _generate_previews(asset, preview_url):
    if not generate_previews(asset.id, preview_url):
        asset.update_preview(preview_status='error')
