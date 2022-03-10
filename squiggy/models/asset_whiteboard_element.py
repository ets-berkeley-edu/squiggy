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
from squiggy import db, std_commit
from squiggy.models.base import Base


class AssetWhiteboardElement(Base):
    __tablename__ = 'asset_whiteboard_elements'

    # Tracks whiteboards which were exported to Asset Library.
    asset_id = db.Column(Integer, ForeignKey('assets.id'), primary_key=True)
    element = db.Column(JSONB, nullable=False)
    element_asset_id = db.Column(Integer, ForeignKey('assets.id'))
    uid = db.Column(db.String(255), nullable=False, primary_key=True)

    def __init__(
            self,
            element,
            uid,
            asset_id=None,
            element_asset_id=None,
    ):
        self.asset_id = asset_id
        self.element = element
        self.element_asset_id = element_asset_id
        self.uid = uid

    @classmethod
    def create(cls, asset_id, whiteboard_elements):
        for whiteboard_element in whiteboard_elements:
            asset_whiteboard_element = cls(
                asset_id=asset_id,
                element=whiteboard_element.element,
                element_asset_id=whiteboard_element.asset_id,
                uid=whiteboard_element.uid,
            )
            db.session.add(asset_whiteboard_element)
        std_commit()

    @classmethod
    def find_by_asset_id(cls, asset_id):
        return cls.query.filter_by(asset_id=asset_id).all()

    def to_api_json(self):
        return {
            'assetId': self.asset_id,
            'element': self.element,
            'elementAssetId': self.element_asset_id,
            'uid': self.uid,
        }
