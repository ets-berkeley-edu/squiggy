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

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from squiggy import db, std_commit
from squiggy.lib.util import utc_now
from squiggy.models.base import Base


class AssetWhiteboardElement(Base):
    __tablename__ = 'asset_whiteboard_elements'

    # Tracks whiteboards which were exported to Asset Library.
    asset_id = db.Column(Integer, ForeignKey('assets.id'), primary_key=True)
    element = db.Column(JSONB, nullable=False)
    element_asset_id = db.Column(Integer, ForeignKey('assets.id'))
    uuid = db.Column(db.String(255), nullable=False, primary_key=True)
    z_index = db.Column('z_index', Integer, nullable=False)
    # Override created_at in base class with primary key notation.
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, primary_key=True)

    def __init__(
            self,
            element,
            uuid,
            z_index,
            asset_id=None,
            element_asset_id=None,
    ):
        self.asset_id = asset_id
        self.element = element
        self.element_asset_id = element_asset_id
        self.uuid = uuid
        self.z_index = z_index

    @classmethod
    def create(
            cls,
            asset_id,
            element,
            element_asset_id,
            uuid,
            z_index,
    ):
        db.session.add(
            cls(
                asset_id=asset_id,
                element=element,
                element_asset_id=element_asset_id,
                uuid=uuid,
                z_index=z_index,
            ),
        )
        std_commit()

    @classmethod
    def delete(cls, asset_id, uuid):
        db.session.query(cls).filter_by(asset_id=asset_id, uuid=uuid).delete()
        std_commit()

    @classmethod
    def find_by_asset_id(cls, asset_id):
        return cls.query.filter_by(asset_id=asset_id).all()

    def to_api_json(self):
        return {
            'assetId': self.asset_id,
            'element': self.element,
            'elementAssetId': self.element_asset_id,
            'uuid': self.uuid,
            'zIndex': self.z_index,
        }
