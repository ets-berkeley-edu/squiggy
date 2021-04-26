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

from datetime import datetime
from time import sleep

from flask import current_app as app
from sqlalchemy import nullsfirst
from squiggy import db, std_commit
from squiggy.externals.canvas import get_canvas
from squiggy.lib.background_job import BackgroundJob
from squiggy.models.canvas_poller_api_key import CanvasPollerApiKey
from squiggy.models.category import Category
from squiggy.models.course import Course
from squiggy.models.user import User


def launch_pollers():
    keys = CanvasPollerApiKey.query.all()
    app.logger.info(f'Will start {len(keys)} poller instances')
    for key in keys:
        CanvasPoller(canvas_api_domain=key.canvas_api_domain, api_key=key.api_key).run_async()


class CanvasPoller(BackgroundJob):

    def run(self, canvas_api_domain, api_key):
        app.logger.info(f'New poller running for {canvas_api_domain}')
        api_url = f'https://{canvas_api_domain}'
        self.canvas = get_canvas(api_url, api_key)

        while True:
            course = db.session.query(Course) \
                .filter_by(canvas_api_domain=canvas_api_domain, active=True) \
                .order_by(nullsfirst(Course.last_polled.asc())) \
                .with_for_update() \
                .first()
            app.logger.info(f"Will poll {_format_course(course)}, last polled {course.last_polled or 'never'}")
            course.last_polled = datetime.now()
            db.session.add(course)
            std_commit()

            try:
                self.poll_course(course)
            except Exception as e:
                app.logger.error(f'Failed to poll course {_format_course(course)}')
                app.logger.exception(e)
            sleep(5)

    def poll_course(self, db_course):
        api_course = self.canvas.get_course(db_course.canvas_course_id)
        if self.poll_tab_configuration(db_course, api_course) is False:
            return
        users_by_canvas_id = self.poll_users(db_course, api_course)
        self.poll_assignments(db_course, api_course, users_by_canvas_id)

    def poll_tab_configuration(self, db_course, api_course):
        tabs = api_course.get_tabs()
        course_updates = {}
        has_active_tools = False

        if db_course.asset_library_url:
            asset_library_tab = next((t for t in tabs if db_course.asset_library_url.endswith(t.html_url)), None)
            if not asset_library_tab or getattr(asset_library_tab, 'hidden', None):
                app.logger.info(f'No active tab found for Asset Library, will remove URL from db: {_format_course(db_course)}')
                course_updates['asset_library_url'] = None
            else:
                has_active_tools = True
        if db_course.engagement_index_url:
            engagement_index_tab = next((t for t in tabs if db_course.engagement_index_url.endswith(t.html_url)), None)
            if not engagement_index_tab or getattr(engagement_index_tab, 'hidden', None):
                app.logger.info(f'No active tab found for Engagement Index, will remove URL from db: {_format_course(db_course)}')
                course_updates['engagement_index_url'] = None
            else:
                has_active_tools = True

        if not has_active_tools:
            app.logger.info(f'No active tools found for course, will mark inactive: {_format_course(db_course)}')
            course_updates['active'] = False

        if course_updates:
            for key, value in course_updates.items():
                setattr(db_course, key, value)
            db.session.add(db_course)
            std_commit()

        return course_updates.get('active', True)

    def poll_users(self, db_course, api_course):  # noqa C901
        db_users_by_canvas_id = {u.canvas_user_id: u for u in db_course.users}

        api_sections = list(api_course.get_sections(include=['students']))
        app.logger.info(f'Retrieved {len(api_sections)} sections from Canvas: {_format_course(db_course)}')
        api_sections_by_user_id = {}
        for s in api_sections:
            for u in s.students:
                user_id = u['id']
                if api_sections_by_user_id.get(user_id):
                    api_sections_by_user_id[user_id].append(s.name)
                else:
                    api_sections_by_user_id[user_id] = [s.name]

        api_users = list(api_course.get_users(include=['enrollments', 'avatar_url', 'email']))
        app.logger.info(f'Retrieved {len(api_users)} users from Canvas: {_format_course(db_course)}')
        api_user_ids = set()
        for u in api_users:
            api_user_ids.add(u.id)
            enrollment_state = 'active'
            course_role = 'Student'
            enrollment = next((e for e in u.enrollments if e['course_id'] == db_course.canvas_course_id), None)
            if not enrollment:
                enrollment_state = 'completed'
            else:
                if enrollment['enrollment_state'] in ['active', 'completed', 'inactive', 'invited', 'rejected']:
                    enrollment_state = enrollment['enrollment_state']
                if enrollment['role'] in ['Adv Designer', 'DesignerEnrollment', 'TaEnrollment', 'TeacherEnrollment']:
                    course_role = 'urn:lti:role:ims/lis/Instructor'

            user_attributes = {
                'canvas_course_role': course_role,
                'canvas_enrollment_state': enrollment_state,
                'canvas_full_name': u.name,
                'canvas_user_id': u.id,
                'course_id': db_course.id,
                'canvas_course_sections': api_sections_by_user_id.get(u.id, []),
                'canvas_email': getattr(u, 'email', None),
                'canvas_image': getattr(u, 'avatar_url', None),
            }
            db_user = db_users_by_canvas_id.get(u.id)
            if not db_user:
                app.logger.debug(f'Adding new user {u.id}: {_format_course(db_course)}')
                db_users_by_canvas_id[u.id] = User.create(**user_attributes)
            else:
                updated = False
                for key, value in user_attributes.items():
                    if getattr(db_user, key, None) != value:
                        setattr(db_user, key, value)
                        updated = True
                if updated:
                    app.logger.debug(f'Updating info for user {db_user.canvas_user_id}: {_format_course(db_course)}')
                    db.session.add(db_user)
                    std_commit()

        for db_user in db_users_by_canvas_id.values():
            if db_user.canvas_user_id not in api_user_ids and db_user.canvas_enrollment_state != 'inactive':
                app.logger.debug(f'Marking user {db_user.canvas_user_id} as inactive: {_format_course(db_course)}')
                db_user.canvas_enrollment_state = 'inactive'
                db.session.add(db_user)
        std_commit()
        return db_users_by_canvas_id

    def poll_assignments(self, db_course, api_course, users_by_canvas_id):
        course_categories = Category.query.filter_by(course_id=db_course.id).all()
        assignments = list(api_course.get_assignments())
        app.logger.info(f'Retrieved {len(assignments)} assignments from Canvas: {_format_course(db_course)}')
        for assignment in assignments:
            # Ignore unpublished assignments.
            if not getattr(assignment, 'published', None):
                continue
            # Don't create submission activities for assigned discussions.
            submission_types = getattr(assignment, 'submission_types', [])
            if 'discussion_topic' in submission_types:
                continue

            assignment_category = next((c for c in course_categories if c.canvas_assignment_id == assignment.id), None)
            is_syncable = 'online_url' in submission_types or 'online_upload' in submission_types
            if not is_syncable and not assignment_category:
                app.logger.debug(f'Skipping non-syncable assignment (id {assignment.id}) with no associated category: {_format_course(db_course)}')
                continue

            # If the assignment is not syncable and the associated category exists but has no assets, remove it from the
            # database.
            if not is_syncable and len(assignment_category.assets) == 0:
                db.session.delete(assignment_category)
                std_commit()

            # Create a category for an assignment if it doesn't exist yet, by default not visible.
            if not assignment_category:
                assignment_category = Category.create(
                    canvas_assignment_name=assignment.name,
                    course_id=db_course.id,
                    title=assignment.name,
                    canvas_assignment_id=assignment.id,
                    visible=False,
                )
            # Update the category title if the assignment name has changed and there has been no manual update.
            elif assignment_category.canvas_assignment_name != assignment.name:
                if assignment_category.title == assignment_category.canvas_assignment_name:
                    assignment_category.title = assignment.name
                    assignment_category.canvas_assignment_name = assignment.name
                    db.session.add(assignment_category)
                    std_commit()

            self.poll_assignment_submissions(db_course, api_course, users_by_canvas_id)

        # Remove any empty categories no longer corresponding to an active assignment.
        for course_category in Category.query.filter_by(course_id=db_course.id).all():
            if len(course_category.assets) == 0:
                db.session.delete(course_category)
                std_commit()

    def poll_assignment_submissions(self, db_course, api_course, users_by_canvas_id):
        pass


def _format_course(course):
    return f'course {course.canvas_course_id}, {course.canvas_api_domain}'
