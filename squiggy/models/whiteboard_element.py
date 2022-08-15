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

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import asc, text
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.asset import Asset
from squiggy.models.base import Base
from squiggy.models.whiteboard_session import WhiteboardSession


class WhiteboardElement(Base):
    __tablename__ = 'whiteboard_elements'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    asset_id = db.Column('asset_id', Integer, ForeignKey('assets.id'))
    element = db.Column('element', JSONB, nullable=False)
    uuid = db.Column('uuid', db.String(255), nullable=False)
    whiteboard_id = db.Column('whiteboard_id', Integer, ForeignKey('whiteboards.id'), nullable=False)
    z_index = db.Column('z_index', Integer, nullable=False)

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
            z_index,
    ):
        self.asset_id = asset_id
        self.element = element
        self.uuid = uuid
        self.whiteboard_id = whiteboard_id
        self.z_index = z_index

    @classmethod
    def find_by_uuid(cls, uuid, whiteboard_id):
        return cls.query.filter_by(uuid=uuid, whiteboard_id=whiteboard_id).first()

    @classmethod
    def find_by_whiteboard_id(cls, whiteboard_id):
        results = cls.query.filter_by(whiteboard_id=whiteboard_id).all()
        asset_ids = [r.asset_id for r in results if r.asset_id]
        # No deleted assets allowed on whiteboards.
        if asset_ids:
            deleted_asset_ids = {r[0] for r in db.session.query(Asset.id).filter(Asset.id.in_(asset_ids), Asset.deleted_at.isnot(None)).all()}
            if deleted_asset_ids:
                results = [r for r in results if not r.asset_id or r.asset_id not in deleted_asset_ids]
        return results

    @classmethod
    def get_id_per_uuid(cls, uuid):
        query = text('SELECT id FROM whiteboard_elements WHERE uuid = :uuid')
        result = db.session.execute(query, {'uuid': uuid}).first()
        std_commit()
        return result and result['id']

    @classmethod
    def get_live_asset_usages(cls, asset_id):
        query = cls.query.filter_by(asset_id=asset_id).join(WhiteboardSession, cls.whiteboard_id == WhiteboardSession.whiteboard_id)
        return [r.to_api_json() for r in query.all()]

    @classmethod
    def create(cls, element, uuid, whiteboard_id, z_index, asset_id=None):
        # Ensure consistent uuid.
        element['uuid'] = uuid

        whiteboard_element = cls(
            asset_id=asset_id,
            element=element,
            uuid=uuid,
            whiteboard_id=whiteboard_id,
            z_index=z_index,
        )
        db.session.add(whiteboard_element)
        std_commit()
        return whiteboard_element

    @classmethod
    def delete(cls, uuid, whiteboard_id):
        db.session.query(cls).filter_by(uuid=uuid, whiteboard_id=whiteboard_id).delete()
        std_commit()

    @classmethod
    def update(cls, element, uuid, whiteboard_id, asset_id=None):
        whiteboard_element = cls.query.filter_by(uuid=uuid, whiteboard_id=whiteboard_id).first()
        if whiteboard_element:
            whiteboard_element.asset_id = asset_id

            # Ensure consistent uuid.
            element['uuid'] = uuid
            whiteboard_element.element = element

            db.session.add(whiteboard_element)
            std_commit()
            return whiteboard_element

    @classmethod
    def update_order(cls, direction, uuids, whiteboard_id):
        whiteboard_elements = cls.query.filter(cls.whiteboard_id == whiteboard_id).order_by(asc(cls.z_index)).all()
        selected = list(filter(lambda w: w.uuid in uuids, whiteboard_elements))
        others = list(filter(lambda w: w.uuid not in uuids, whiteboard_elements))
        z_index = 0
        if direction == 'bringForward':
            # TODO: Implement this if customer convinces us to expand the layering feature.
            pass
        elif direction == 'bringToFront':
            for whiteboard_element in others:
                whiteboard_element.z_index = z_index
                z_index += 1
            for whiteboard_element in selected:
                whiteboard_element.z_index = z_index
                z_index += 1
        elif direction == 'sendToBack':
            for whiteboard_element in selected:
                whiteboard_element.z_index = z_index
                z_index += 1
            for whiteboard_element in others:
                whiteboard_element.z_index = z_index
                z_index += 1
        elif direction == 'sendBackwards':
            # TODO: Implement this if customer convinces us to expand the layering feature.
            pass

    def to_api_json(self):
        # Correct any out-of-sync uuid surprises.
        if self.element['uuid'] != self.uuid:
            self.element['uuid'] = self.uuid
            flag_modified(self, 'element')
            std_commit()
        return {
            'id': self.id,
            'assetId': self.asset_id,
            'createdAt': isoformat(self.created_at),
            'element': self.element,
            'updatedAt': isoformat(self.updated_at),
            'uuid': self.uuid,
            'whiteboardId': self.whiteboard_id,
            'zIndex': self.z_index,
        }
