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

from time import sleep
from urllib.request import urlopen

from flask import current_app as app
from sqlalchemy import nullsfirst
from sqlalchemy.orm import joinedload
from squiggy import db, std_commit
from squiggy.externals.canvas import get_canvas
from squiggy.lib.background_job import BackgroundJob
from squiggy.lib.util import utc_now
from squiggy.logger import initialize_background_logger, logger
from squiggy.models.activity import Activity
from squiggy.models.asset import Asset
from squiggy.models.canvas_poller_api_key import CanvasPollerApiKey
from squiggy.models.category import Category
from squiggy.models.course import Course
from squiggy.models.user import User


def launch_pollers():
    keys = CanvasPollerApiKey.query.all()
    logger.info(f'Will start {len(keys)} poller instances')
    for (i, key) in enumerate(keys):
        CanvasPoller(poller_id=i, canvas_api_domain=key.canvas_api_domain, api_key=key.api_key).run_async()


class CanvasPoller(BackgroundJob):

    def __init__(self, poller_id, **kwargs):
        thread_name = f'poller-{poller_id}'
        initialize_background_logger(
            name=thread_name,
            location=f"poller_{poller_id}_{kwargs.get('canvas_api_domain')}.log",
        )
        super().__init__(thread_name=thread_name, **kwargs)

    def run(self, canvas_api_domain, api_key):
        logger.info(f'New poller running for {canvas_api_domain}')
        api_url = f'https://{canvas_api_domain}'
        self.canvas = get_canvas(api_url, api_key)

        while True:
            course = db.session.query(Course) \
                .filter_by(canvas_api_domain=canvas_api_domain, active=True) \
                .order_by(nullsfirst(Course.last_polled.asc())) \
                .with_for_update() \
                .first()
            if not course:
                logger.info(f'No active courses found: {canvas_api_domain}')
            else:
                logger.info(f"Will poll {_format_course(course)}, last polled {course.last_polled or 'never'}")
                course.last_polled = utc_now()
                db.session.add(course)
                std_commit()

                try:
                    self.poll_course(course)
                except Exception as e:
                    logger.error(f'Failed to poll course {_format_course(course)}')
                    logger.exception(e)
            sleep(5)

    def poll_course(self, db_course):
        api_course = self.canvas.get_course(db_course.canvas_course_id)
        if self.poll_tab_configuration(db_course, api_course) is False:
            return
        users_by_canvas_id = self.poll_users(db_course, api_course)
        self.poll_assignments(db_course, api_course, users_by_canvas_id)
        self.poll_discussions(db_course, api_course, users_by_canvas_id)
        self.poll_last_activity(db_course)

    def poll_tab_configuration(self, db_course, api_course):
        tabs = api_course.get_tabs()
        course_updates = {}
        has_active_tools = False

        if db_course.asset_library_url:
            asset_library_tab = next((t for t in tabs if db_course.asset_library_url.endswith(t.html_url)), None)
            if not asset_library_tab or getattr(asset_library_tab, 'hidden', None):
                logger.info(f'No active tab found for Asset Library, will remove URL from db: {_format_course(db_course)}')
                course_updates['asset_library_url'] = None
            else:
                has_active_tools = True
        if db_course.engagement_index_url:
            engagement_index_tab = next((t for t in tabs if db_course.engagement_index_url.endswith(t.html_url)), None)
            if not engagement_index_tab or getattr(engagement_index_tab, 'hidden', None):
                logger.info(f'No active tab found for Engagement Index, will remove URL from db: {_format_course(db_course)}')
                course_updates['engagement_index_url'] = None
            else:
                has_active_tools = True

        if not has_active_tools:
            logger.info(f'No active tools found for course, will mark inactive: {_format_course(db_course)}')
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
        logger.info(f'Retrieved {len(api_sections)} sections from Canvas: {_format_course(db_course)}')
        api_sections_by_user_id = {}
        for s in api_sections:
            for u in (s.students or []):
                user_id = u['id']
                if api_sections_by_user_id.get(user_id):
                    api_sections_by_user_id[user_id].append(s.name)
                else:
                    api_sections_by_user_id[user_id] = [s.name]

        api_users = list(api_course.get_users(include=['enrollments', 'avatar_url', 'email']))
        logger.info(f'Retrieved {len(api_users)} users from Canvas: {_format_course(db_course)}')
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
                logger.debug(f'Adding new user {u.id}: {_format_course(db_course)}')
                db_users_by_canvas_id[u.id] = User.create(**user_attributes)
            else:
                updated = False
                for key, value in user_attributes.items():
                    if getattr(db_user, key, None) != value:
                        setattr(db_user, key, value)
                        updated = True
                if updated:
                    logger.debug(f'Updating info for user {db_user.canvas_user_id}: {_format_course(db_course)}')
                    db.session.add(db_user)
                    std_commit()

        for db_user in db_users_by_canvas_id.values():
            if db_user.canvas_user_id not in api_user_ids and db_user.canvas_enrollment_state != 'inactive':
                logger.debug(f'Marking user {db_user.canvas_user_id} as inactive: {_format_course(db_course)}')
                db_user.canvas_enrollment_state = 'inactive'
                db.session.add(db_user)
        std_commit()
        return db_users_by_canvas_id

    def poll_assignments(self, db_course, api_course, users_by_canvas_id):
        course_categories = Category.query.filter_by(course_id=db_course.id).all()
        assignments = list(api_course.get_assignments())
        logger.info(f'Retrieved {len(assignments)} assignments from Canvas: {_format_course(db_course)}')
        assignment_ids = set()
        for assignment in assignments:
            # Ignore unpublished assignments.
            if not getattr(assignment, 'published', None):
                continue
            # Don't create submission activities for assigned discussions.
            submission_types = getattr(assignment, 'submission_types', [])
            if 'discussion_topic' in submission_types:
                continue

            assignment_ids.add(assignment.id)
            assignment_category = next((c for c in course_categories if c.canvas_assignment_id == assignment.id), None)
            is_syncable = 'online_url' in submission_types or 'online_upload' in submission_types
            if not is_syncable and not assignment_category:
                logger.debug(f'Skipping non-syncable assignment (id {assignment.id}) with no associated category: {_format_course(db_course)}')
                continue

            # If the assignment is not syncable and the associated category exists but has no assets, remove it from the
            # database.
            if not is_syncable and len(assignment_category.assets) == 0:
                db.session.delete(assignment_category)
                std_commit()
                continue

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

            self.poll_assignment_submissions(assignment, assignment_category, db_course, api_course, users_by_canvas_id)

        # Remove any empty categories no longer corresponding to an active assignment.
        for course_category in Category.query.filter_by(course_id=db_course.id).all():
            if (
                course_category.canvas_assignment_id
                and course_category.canvas_assignment_id not in assignment_ids
                and not len(course_category.assets)
            ):
                db.session.delete(course_category)
                std_commit()

    def poll_assignment_submissions(self, assignment, category, db_course, api_course, users_by_canvas_id):
        if not getattr(assignment, 'has_submitted_submissions', False):
            logger.debug(f'Ignoring assignment (id {assignment.id}) without submissions: {_format_course(db_course)}')
            return

        def _is_submission_active(s):
            pending_states = ['unsubmitted', 'pending_upload']
            if getattr(s, 'workflow_state', None) in pending_states:
                return False
            # A file upload submission is ready for processing only if all file attachments are ready.
            if getattr(s, 'submission_type', None) == 'online_upload':
                attachments = getattr(s, 'attachments', [])
                for attachment in attachments:
                    if getattr(s, 'workflow_state', None) in pending_states:
                        return False
            return True

        submissions = list(assignment.get_submissions())
        active_submissions = [s for s in submissions if _is_submission_active(s)]
        logger.info(
            f'Got {len(submissions)} submissions, will process {len(active_submissions)} active submissions: '
            f'assignment {assignment.id}, {_format_course(db_course)}')
        if len(active_submissions) > 0:
            self.sync_submissions(db_course, category, assignment, active_submissions, users_by_canvas_id)

    def sync_submissions(self, course, category, assignment, submissions, users_by_canvas_id):
        activity_index = self.index_activities(
            Activity.query.filter_by(
                course_id=course.id,
                activity_type='assignment_submit',
                object_type='canvas_submission',
                object_id=assignment.id,
            ).options(
                joinedload(Activity.user),
            ),
        )
        file_submission_tracker = {}
        link_submission_tracker = {}

        for submission in submissions:
            # Skip if the user is no longer in the course.
            canvas_user_id = getattr(submission, 'user_id', None)
            submission_user = users_by_canvas_id.get(canvas_user_id, None)
            if not submission_user:
                continue

            sync_assets = self.handle_submission_activities(course, submission_user, category, assignment, submission, activity_index)
            if sync_assets is False:
                continue

            previous_submissions = submission_user.assets.filter_by(canvas_assignment_id=assignment.id, deleted_at=None).all()
            if previous_submissions:
                for s in previous_submissions:
                    s.deleted_at = utc_now()
                    db.session.add(s)
                logger.debug(
                    f'Deleted {len(previous_submissions)} assets for older submissions: '
                    f'user {canvas_user_id}, assignment {assignment.id}, {_format_course(course)}')

            # If sync is not enabled for this assignment, return without pulling down any new attachments.
            if not category.visible:
                continue

            submission_type = getattr(submission, 'submission_type', None)
            if submission_type == 'online_url':
                self.create_link_submission_asset(course, submission_user, category, assignment, submission, link_submission_tracker)
            elif submission_type == 'online_upload':
                self.create_file_submission_assets(course, submission_user, category, assignment, submission, file_submission_tracker)

    def handle_submission_activities(self, course, user, category, assignment, submission, activity_index):
        submission_metadata = {
            'submission_id': submission.id,
            'attempt': getattr(submission, 'attempt', None),
            'file_sync_enabled': category.visible,
        }
        activity_index[user.canvas_user_id] = activity_index.get(user.canvas_user_id, {})
        activity_index[user.canvas_user_id]['assignment_submit'] = activity_index[user.canvas_user_id].get('assignment_submit', {})
        existing_activity = activity_index[user.canvas_user_id]['assignment_submit'].get(assignment.id, None)
        if existing_activity:
            # If we've already seen this submission attempt and there's been no change in visibility settings,
            # skip submission processing.
            if (
                existing_activity.activity_metadata
                and existing_activity.activity_metadata.get('attempt', None) == submission_metadata['attempt']
                and existing_activity.activity_metadata.get('file_sync_enabled', None) == submission_metadata['file_sync_enabled']
            ):
                return False
            # Otherwise the existing activity needs updating and the submission should be processed.
            else:
                existing_activity.activity_metadata = submission_metadata
                db.session.add(existing_activity)
                std_commit()
                return True
        else:
            activity_index[user.canvas_user_id]['assignment_submit'][assignment.id] = Activity.create(
                activity_type='assignment_submit',
                course_id=course.id,
                user_id=user.id,
                object_type='canvas_submission',
                object_id=assignment.id,
                activity_metadata=submission_metadata,
            )
            return True

    def create_link_submission_asset(self, course, user, category, assignment, submission, link_submission_tracker):
        try:
            existing_submission_asset = link_submission_tracker.get(submission.url, None)
            if existing_submission_asset:
                logger.debug(f'Adding new user to existing link asset: user {user.canvas_user_id}, asset {existing_submission_asset.id}.')
                existing_submission_asset.users.append(user)
                db.session.add(existing_submission_asset)
                std_commit()
            else:
                logger.info(
                    f'Will create link asset for submission: '
                    f'user {user.canvas_user_id}, submission {submission.id}, assignment {assignment.id}, {_format_course(course)}')
                link_submission_tracker[submission.url] = Asset.create(
                    asset_type='link',
                    canvas_assignment_id=assignment.id,
                    categories=[category],
                    course_id=course.id,
                    source=submission.url,
                    title=submission.url,
                    url=submission.url,
                    users=[user],
                    create_activity=False,
                )
        except Exception as e:
            logger.error(
                f'Failed to create link asset for an assignment submission: '
                f'user {user.canvas_user_id}, submission {submission.id}, assignment {assignment.id}, {_format_course(course)}')
            logger.exception(e)

    def create_file_submission_assets(self, course, user, category, assignment, submission, file_submission_tracker):
        logger.info(
            f'Will create file assets for submission attachments: '
            f'user {user.canvas_user_id}, submission {submission.id}, assignment {assignment.id}, {_format_course(course)}')
        for attachment in getattr(submission, 'attachments', []):
            try:
                if attachment['size'] > 10485760:
                    logger.debug('Attachment too large, will not process.')
                    continue
                existing_submission_asset = file_submission_tracker.get(attachment['id'], None)
                if existing_submission_asset:
                    logger.debug(f'Adding new user to existing file asset: user {user.canvas_user_id}, asset {existing_submission_asset.id}.')
                    existing_submission_asset.users.append(user)
                    db.session.add(existing_submission_asset)
                    std_commit()
                else:
                    s3_attrs = Asset.upload_to_s3(
                        filename=attachment['filename'],
                        byte_stream=urlopen(attachment['url']).read(),
                        course_id=course.id,
                    )
                    file_submission_tracker[attachment['id']] = Asset.create(
                        asset_type='file',
                        canvas_assignment_id=assignment.id,
                        categories=[category],
                        course_id=course.id,
                        download_url=s3_attrs.get('download_url', None),
                        mime=s3_attrs.get('content_type', None),
                        title=attachment['filename'],
                        users=[user],
                        create_activity=False,
                    )
            except Exception as e:
                logger.error(
                    f'Failed to create file asset for an attachment: '
                    f'user {user.canvas_user_id}, submission {submission.id}, assignment {assignment.id}, {_format_course(course)}')
                logger.exception(e)

    def poll_discussions(self, db_course, api_course, users_by_canvas_id):
        discussion_topics = list(api_course.get_discussion_topics())
        if not discussion_topics:
            return

        logger.info(f'Retrieved {len(discussion_topics)} discussion topics from Canvas: {_format_course(db_course)}')
        discussion_activity_index = self.index_activities(
            Activity.query.filter(
                Activity.course_id == db_course.id,
                Activity.activity_type.in_(['discussion_entry', 'discussion_topic', 'get_discussion_entry_reply']),
            ).options(
                joinedload(Activity.user),
            ),
        )
        for topic in discussion_topics:
            try:
                if not getattr(topic, 'published', False):
                    continue
                # Don't create a discussion_topic for an assigned discussion as these are set up by instructors.
                if not getattr(topic, 'assignment', None):
                    if not discussion_activity_index.get(topic.author.get('id', None), {}).get('discussion_topic', {}).get(topic.id):
                        user = users_by_canvas_id.get(topic.author.get('id', None), None)
                        if user:
                            Activity.create(
                                activity_type='discussion_topic',
                                course_id=db_course.id,
                                user_id=user.id,
                                object_type='canvas_discussion',
                                object_id=topic.id,
                            )
                if not getattr(topic, 'discussion_subentry_count', 0):
                    continue
                entries = list(topic.get_topic_entries())
                logger.info(f'Retrieved {len(entries)} discussion topics from Canvas: discussion {topic.id}, {_format_course(db_course)}')
                for entry in entries:
                    self.create_discussion_entry_activities(entry, topic, db_course, users_by_canvas_id, discussion_activity_index)
            except Exception as e:
                logger.error(f'Failed to poll a discussion topic: topic {topic.id}, {_format_course(db_course)}')
                logger.exception(e)

    def create_discussion_entry_activities(self, entry, topic, course, users_by_canvas_id, discussion_activity_index):
        # Users creating an entry on their own topic get no activity credit.
        if entry.user_id != topic.author.get('id', None):
            if not discussion_activity_index.get(entry.user_id, {}).get('discussion_entry', {}).get(f'{topic.id}_{entry.id}'):
                user = users_by_canvas_id.get(entry.user_id, None)
                if user:
                    Activity.create(
                        activity_type='discussion_entry',
                        course_id=course.id,
                        user_id=user.id,
                        object_type='canvas_discussion',
                        object_id=topic.id,
                        activity_metadata={'entryId': entry.id},
                    )
        replies = list(getattr(entry, 'recent_replies', []))
        for reply in replies:
            parent = entry if entry.id == reply['parent_id'] else next((r for r in replies if r['id'] == reply['parent_id']), None)
            if not parent:
                continue
            parent_user_id = getattr(parent, 'user_id', None) or parent.get('user_id', None)
            reply_user_id = reply.get('user_id', None)
            if not parent_user_id or not reply_user_id or parent_user_id == reply_user_id:
                continue
            parent_user = users_by_canvas_id.get(parent_user_id, None)
            reply_user = users_by_canvas_id.get(reply.get('user_id', None), None)
            if not parent_user or not reply_user:
                continue
            reply_entry_activity = discussion_activity_index.get(reply_user_id, {}).get('discussion_entry', {}).get(f'{topic.id}_{entry.id}')
            if not reply_entry_activity:
                reply_entry_activity = Activity.create(
                    activity_type='discussion_entry',
                    course_id=course.id,
                    user_id=reply_user.id,
                    object_type='canvas_discussion',
                    object_id=topic.id,
                    activity_metadata={'entryId': entry.id},
                )
            if not discussion_activity_index.get(parent_user_id, {}).get('get_discussion_entry_reply', {}).get(f'{topic.id}_{entry.id}'):
                Activity.create(
                    activity_type='get_discussion_entry_reply',
                    course_id=course.id,
                    user_id=parent_user.id,
                    object_type='canvas_discussion',
                    object_id=topic.id,
                    actor_id=reply_user.id,
                    reciprocal_id=reply_entry_activity.id,
                    activity_metadata={'entryId': entry.id},
                )

    def poll_last_activity(self, db_course):
        last_activity = Activity.get_last_activity_for_course(course_id=db_course.id)
        if last_activity and (utc_now() - last_activity).days >= app.config['CANVAS_POLLER_DEACTIVATION_THRESHOLD']:
            logger.info(
                f"Last course activity {last_activity} older than {app.config['CANVAS_POLLER_DEACTIVATION_THRESHOLD']} days, deactivating: "
                f'{_format_course(db_course)}')
            db_course.active = False
            db.session.add(db_course)
            std_commit()

    def index_activities(self, query):
        activities = query.all()
        index = {}
        for a in activities:
            activity_key = a.object_id
            if a.activity_type in ['discussion_entry', 'get_discussion_entry_reply']:
                activity_key = f"{activity_key}_{a.activity_metadata.get('entryId', '')}"
            canvas_user_id = a.user.canvas_user_id
            index[canvas_user_id] = index.get(canvas_user_id, {})
            index[canvas_user_id][a.activity_type] = index[canvas_user_id].get(a.activity_type, {})
            index[canvas_user_id][a.activity_type][activity_key] = a
        return index


def _format_course(course):
    return f'course {course.canvas_course_id}, {course.canvas_api_domain}'
