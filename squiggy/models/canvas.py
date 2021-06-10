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
from squiggy import db
from squiggy.models.base import Base


class Canvas(Base):
    __tablename__ = 'canvas'

    canvas_api_domain = db.Column(db.String(255), nullable=False, primary_key=True)
    api_key = db.Column(db.String(255), nullable=False)
    lti_key = db.Column(db.String(255), nullable=False)
    lti_secret = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    supports_custom_messaging = db.Column(db.Boolean, default=False, nullable=False)
    use_https = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(
            self,
            canvas_api_domain,
            api_key,
            lti_key,
            lti_secret,
            name,
            supports_custom_messaging=False,
            use_https=True,
    ):
        self.api_key = api_key
        self.canvas_api_domain = canvas_api_domain
        self.lti_key = lti_key
        self.lti_secret = lti_secret
        self.name = name
        self.supports_custom_messaging = supports_custom_messaging
        self.use_https = use_https

    def __repr__(self):
        return f"""<Course
                    api_key={self.api_key},
                    canvas_api_domain={self.canvas_api_domain},
                    lti_key={self.lti_key},
                    lti_secret={self.lti_secret},
                    name={self.name},
                    supports_custom_messaging={self.supports_custom_messaging},
                    use_https={self.use_https},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    @classmethod
    def find_by_domain(cls, canvas_api_domain):
        return cls.query.filter_by(canvas_api_domain=canvas_api_domain).first()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.name).all()

    def to_api_json(self):
        return {
            'apiKey': self.api_key,
            'canvasApiDomain': self.canvas_api_domain,
            'ltiKey': self.lti_key,
            'ltiSecret': self.lti_secret,
            'name': self.name,
            'supportsCustomMessaging': self.supports_custom_messaging,
            'useHttps': self.use_https,
            'createdAt': _isoformat(self.created_at),
            'updatedAt': _isoformat(self.updated_at),
        }


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
