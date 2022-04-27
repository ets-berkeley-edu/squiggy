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

from sqlalchemy import ForeignKey, Integer, text
from squiggy import db, std_commit
from squiggy.lib.util import isoformat
from squiggy.models.base import Base


class WhiteboardSession(Base):
    __tablename__ = 'whiteboard_sessions'

    socket_id = db.Column('socket_id', db.String(255), nullable=False, primary_key=True)
    user_id = db.Column('user_id', Integer, nullable=False)
    whiteboard_id = db.Column('whiteboard_id', Integer, ForeignKey('whiteboards.id'), nullable=False)

    def __init__(
            self,
            socket_id,
            user_id,
            whiteboard_id,
    ):
        self.socket_id = socket_id
        self.user_id = user_id
        self.whiteboard_id = whiteboard_id

    @classmethod
    def create(cls, socket_id, user_id, whiteboard_id):
        whiteboard_session = cls(
            socket_id=str(socket_id),
            user_id=user_id,
            whiteboard_id=whiteboard_id,
        )
        db.session.add(whiteboard_session)
        std_commit()
        return whiteboard_session

    @classmethod
    def delete(cls, socket_id):
        whiteboard_session = cls.query.filter_by(socket_id=str(socket_id)).first()
        if whiteboard_session:
            db.session.delete(whiteboard_session)
            std_commit()

    @classmethod
    def delete_stale_records(cls, older_than_minutes=5):
        sql = f"DELETE FROM whiteboard_sessions WHERE updated_at < (now() - INTERVAL '{older_than_minutes} minutes')"
        db.session.execute(text(sql))

    @classmethod
    def find(cls, whiteboard_id, user_id=None):
        if user_id:
            filter_by = cls.query.filter_by(user_id=user_id, whiteboard_id=whiteboard_id)
        else:
            filter_by = cls.query.filter_by(whiteboard_id=whiteboard_id)
        return filter_by.all()

    @classmethod
    def find_by_socket_id(cls, socket_id):
        return cls.query.filter_by(socket_id=str(socket_id)).first()

    @classmethod
    def update_updated_at(cls, socket_id):
        db.session.execute(
            text('UPDATE whiteboard_sessions SET updated_at = now() WHERE socket_id = :socket_id'),
            {'socket_id': socket_id},
        )

    def to_api_json(self):
        return {
            'createdAt': isoformat(self.created_at),
            'socketId': self.socket_id,
            'userId': self.user_id,
            'updatedAt': isoformat(self.updated_at),
            'whiteboardId': self.whiteboard_id,
        }
