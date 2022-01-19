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
from squiggy.models.base import Base


class CanvasPollerApiKey(Base):
    __tablename__ = 'canvas_poller_api_keys'

    canvas_api_domain = db.Column(db.String(255), nullable=False, primary_key=True)
    api_key = db.Column(db.String(255), nullable=False, primary_key=True)

    def __init__(
        self,
        canvas_api_domain,
        api_key,
    ):
        self.api_key = api_key
        self.canvas_api_domain = canvas_api_domain

    def __repr__(self):
        return f"""<Course
                    api_key={self.api_key},
                    canvas_api_domain={self.canvas_api_domain}
                """

    @classmethod
    def create(cls, canvas_api_domain, api_key):
        api_key = cls(
            canvas_api_domain=canvas_api_domain,
            api_key=api_key,
        )
        db.session.add(api_key)
        std_commit()
        return api_key

    @classmethod
    def find_by_domain(cls, canvas_api_domain):
        return cls.query.filter_by(canvas_api_domain=canvas_api_domain).all()
