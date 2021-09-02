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
from squiggy import db, std_commit
from squiggy.models.base import Base
from squiggy.models.canvas import Canvas


class Course(Base):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    active = db.Column(db.Boolean, nullable=False)
    asset_library_url = db.Column(db.String(255))
    canvas_api_domain = db.Column(db.String(255), nullable=False)
    canvas_course_id = db.Column(db.Integer, nullable=False)
    enable_daily_notifications = db.Column(db.Boolean, default=True, nullable=False)
    enable_upload = db.Column(db.Boolean, default=True, nullable=False)
    enable_weekly_notifications = db.Column(db.Boolean, default=True, nullable=False)
    engagement_index_url = db.Column(db.String(255))
    name = db.Column(db.String(255))
    last_polled = db.Column(db.DateTime)

    users = db.relationship('User', back_populates='course')

    def __init__(
            self,
            active,
            canvas_api_domain,
            canvas_course_id,
            asset_library_url=None,
            enable_daily_notifications=True,
            enable_upload=True,
            enable_weekly_notifications=True,
            engagement_index_url=None,
            name=None,
    ):
        self.active = active
        self.asset_library_url = asset_library_url
        self.canvas_api_domain = canvas_api_domain
        self.canvas_course_id = canvas_course_id
        self.enable_daily_notifications = enable_daily_notifications
        self.enable_upload = enable_upload
        self.enable_weekly_notifications = enable_weekly_notifications
        self.engagement_index_url = engagement_index_url
        self.name = name

    def __repr__(self):
        return f"""<Course
                    active={self.active},
                    asset_library_url={self.asset_library_url},
                    canvas_api_domain={self.canvas_api_domain},
                    canvas_course_id={self.canvas_course_id},
                    enable_daily_notifications={self.enable_daily_notifications},
                    enable_upload={self.enable_upload},
                    enable_weekly_notifications={self.enable_weekly_notifications},
                    engagement_index_url={self.engagement_index_url},
                    id={self.id},
                    name={self.name},
                    created_at={self.created_at},
                    updated_at={self.updated_at}>
                """

    @classmethod
    def find_by_id(cls, course_id):
        return cls.query.filter_by(id=course_id).first()

    @classmethod
    def find_by_canvas_course_id(cls, canvas_api_domain, canvas_course_id):
        return cls.query.filter_by(canvas_api_domain=canvas_api_domain, canvas_course_id=canvas_course_id).first()

    @classmethod
    def create(
            cls,
            canvas_api_domain,
            canvas_course_id,
            asset_library_url=None,
            engagement_index_url=None,
            name=None,
    ):
        course = cls(
            active=True,
            asset_library_url=asset_library_url,
            canvas_api_domain=canvas_api_domain,
            canvas_course_id=canvas_course_id,
            engagement_index_url=engagement_index_url,
            name=name,
        )
        db.session.add(course)
        std_commit()
        return course

    @classmethod
    def update(
            cls,
            active,
            asset_library_url,
            course_id,
            engagement_index_url,
    ):
        course = cls.find_by_id(course_id=course_id)
        course.active = active
        course.asset_library_url = asset_library_url
        course.engagement_index_url = engagement_index_url
        db.session.add(course)
        std_commit()
        return course

    def to_api_json(self):
        canvas = Canvas.find_by_domain(canvas_api_domain=self.canvas_api_domain)
        return {
            'active': self.active,
            'assetLibraryUrl': self.asset_library_url,
            'canvas': canvas.to_api_json(),
            'canvasApiDomain': self.canvas_api_domain,
            'canvasCourseId': self.canvas_course_id,
            'enableDailyNotifications': self.enable_daily_notifications,
            'enableUpload': self.enable_upload,
            'enableWeeklyNotifications': self.enable_weekly_notifications,
            'engagementIndexUrl': self.engagement_index_url,
            'id': self.id,
            'name': self.name,
            'lastPolled': _isoformat(self.last_polled),
            'createdAt': _isoformat(self.created_at),
            'updatedAt': _isoformat(self.updated_at),
        }

    def activate(self):
        self.active = True
        db.session.add(self)
        std_commit()


def _isoformat(value):
    return value and value.astimezone(tzutc()).isoformat()
