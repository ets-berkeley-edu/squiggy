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

from uuid import uuid4

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.base import Base


class WhiteboardElement(Base):
    __tablename__ = 'whiteboard_elements'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    asset_id = db.Column('asset_id', Integer, ForeignKey('assets.id'))
    element = db.Column('element', JSONB, nullable=False)
    uuid = db.Column('uuid', db.String(255), nullable=False)
    whiteboard_id = db.Column('whiteboard_id', Integer, ForeignKey('whiteboards.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint(
        'created_at',
        'uuid',
        'whiteboard_id',
        name='whiteboard_elements_created_at_uuid_whiteboard_id_idx',
    ),)

    def __init__(
            self,
            asset_id,
            element,
            uuid,
            whiteboard_id,
    ):
        self.asset_id = asset_id
        self.element = element
        self.uuid = uuid
        self.whiteboard_id = whiteboard_id

    @classmethod
    def find_by_whiteboard_id(cls, whiteboard_id):
        return cls.query.filter_by(whiteboard_id=whiteboard_id).all()

    @classmethod
    def create(cls, element, whiteboard_id, asset_id=None):
        uuid = str(uuid4())
        asset_whiteboard_element = cls(
            asset_id=asset_id,
            element={
                **element,
                'uuid': uuid,
            },
            uuid=uuid,
            whiteboard_id=whiteboard_id,
        )
        db.session.add(asset_whiteboard_element)
        std_commit()
        return asset_whiteboard_element

    @classmethod
    def delete(cls, uuid, whiteboard_id):
        db.session.query(cls).filter_by(uuid=uuid, whiteboard_id=whiteboard_id).delete()
        std_commit()

    @classmethod
    def update(cls, element, uuid, whiteboard_id, asset_id=None):
        whiteboard_element = cls.query.filter_by(uuid=uuid, whiteboard_id=whiteboard_id).first()
        whiteboard_element.asset_id = asset_id
        whiteboard_element.element = element
        db.session.add(whiteboard_element)
        std_commit()
        return whiteboard_element

    def to_api_json(self):
        return {
            'id': self.id,
            'assetId': self.asset_id,
            'createdAt': isoformat(self.created_at),
            'element': self.element,
            'updatedAt': isoformat(self.updated_at),
            'uuid': self.uuid,
            'whiteboardId': self.whiteboard_id,
        }
