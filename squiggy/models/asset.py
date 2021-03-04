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

from dateutil.tz import tzutc
from flask import current_app as app
from sqlalchemy.dialects.postgresql import ENUM
from squiggy import db, std_commit
from squiggy.models.base import Base


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
    course_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    title = db.Column(db.String(255))
    uid = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255))
    visible = db.Column(db.Boolean, nullable=False)

    def __init__(
            self,
            asset_type,
            course_id,
            uid,
            description=None,
            title=None,
            url=None,
            visible=True,
    ):
        self.asset_type = asset_type
        self.course_id = course_id
        self.description = description
        self.title = title
        self.uid = uid
        self.url = url
        self.visible = visible

    def __repr__(self):
        return f"""<Asset
                    asset_type={self.asset_type},
                    course_id={self.course_id},
                    description={self.description},
                    title={self.title},
                    uid={self.uid},
                    url={self.url},
                    visible={self.visible},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    def to_api_json(self):
        return {
            'courseId': self.course_id,
            'description': self.description,
            'title': self.title,
            'type': self.asset_type,
            'uid': self.uid,
            'url': self.url,
            'visible': self.visible,
            'createdAt': _isoformat(self.created_at),
            'updatedAt': _isoformat(self.updated_at),
        }

    @classmethod
    def create(cls, asset_type, category_id, course_id, description, title, url):
        asset = cls(
            asset_type=asset_type,
            course_id=course_id,
            description=description,
            title=title,
            url=url,
        )
        app.logger.warn(f'TODO: category_id={category_id}')
        db.session.flush()
        std_commit()
        return asset.to_api_json()


def _isoformat(obj, key):
    value = obj.get(key)
    return value and value.astimezone(tzutc()).isoformat()
