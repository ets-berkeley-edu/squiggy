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

from functools import wraps

from flask import current_app as app, redirect, request
from flask_login import current_user, login_user
from flask_socketio import emit
from squiggy.lib.errors import BadRequestError, UnauthorizedRequestError
from squiggy.lib.http import tolerant_jsonify
from squiggy.lib.util import get_user_id, is_admin, is_teaching, safe_strip
from squiggy.lib.whiteboard_housekeeping import WhiteboardHousekeeping
from squiggy.logger import logger
from squiggy.models.activity import Activity
from squiggy.models.activity_type import activities_type
from squiggy.models.asset import Asset, assets_type
from squiggy.models.canvas import Canvas
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement
from squiggy.models.whiteboard_session import WhiteboardSession

SOCKET_IO_NAMESPACE = '/'


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        if current_user.is_admin:
            return func(*args, **kw)
        else:
            logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def feature_flag_whiteboards(func):
    @wraps(func)
    def _feature_flag_required(*args, **kw):
        if app.config['FEATURE_FLAG_WHITEBOARDS']:
            return func(*args, **kw)
        else:
            logger.warning('Feature flag is false.')
            return app.login_manager.unauthorized()
    return _feature_flag_required


def teacher_required(func):
    @wraps(func)
    def _teacher_required(*args, **kw):
        is_authorized = current_user.is_authenticated and (current_user.is_admin or current_user.is_teaching)
        if is_authorized:
            return func(*args, **kw)
        else:
            logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _teacher_required


def activities_type_enums():
    return _filter_per_feature_flag(activities_type.enums)


def assets_type_enums():
    return _filter_per_feature_flag(assets_type.enums)


def can_update_asset(user, asset):
    user_id = get_user_id(user)
    user_ids = [user.id for user in asset.users]
    return user.course.id == asset.course_id and (is_teaching(user) or is_admin(user) or user_id in user_ids)


def can_view_asset(asset, user):
    if user and user.is_admin:
        return True
    if not user or user.course.id != asset.course_id:
        return False
    return asset.visible or (asset.id in [a.id for a in current_user.user.assets])


def can_delete_comment(comment, user):
    user_id = get_user_id(user)
    return user_id and (comment.user_id == user_id or user.is_admin or user.is_teaching)


def can_update_comment(comment, user):
    user_id = get_user_id(user)
    return user_id and (comment.user_id == user_id or user.is_admin or user.is_teaching)


def get_socket_io_room(whiteboard_id):
    return f'whiteboard-{whiteboard_id}'


def start_login_session(login_session, redirect_path=None, tool_id=None):
    authenticated = login_user(login_session, remember=True) and current_user.is_authenticated
    if authenticated:
        if redirect_path:
            response = redirect(location=f"{app.config['VUE_LOCALHOST_BASE_URL'] or ''}{redirect_path}")
        else:
            response = tolerant_jsonify(current_user.to_api_json())
        canvas_api_domain = current_user.course.canvas_api_domain
        canvas = Canvas.find_by_domain(canvas_api_domain)
        canvas_course_id = current_user.course.canvas_course_id
        # Yummy cookies!
        key = f'{canvas_api_domain}|{canvas_course_id}'
        value = str(current_user.user_id)
        response.set_cookie(
            key=key,
            value=value,
            samesite='None',
            secure=True,
        )
        response.set_cookie(
            key=f'{canvas_api_domain}_supports_custom_messaging',
            value=str(canvas.supports_custom_messaging),
            samesite='None',
            secure=True,
        )
        return response
    elif tool_id:
        raise UnauthorizedRequestError(f'Unauthorized user during {tool_id} LTI launch (user_id = {login_session.user_id})')
    else:
        return tolerant_jsonify({'message': f'User {login_session.user_id} failed to authenticate.'}, 403)


def upsert_whiteboard_elements(socket_id, whiteboard_elements, whiteboard_id):
    if not Whiteboard.can_update_whiteboard(user=current_user, whiteboard_id=whiteboard_id):
        raise UnauthorizedRequestError('Unauthorized')
    if not socket_id:
        raise BadRequestError('socket_id is required')

    queue_for_preview_image = False
    results = []
    for whiteboard_element in whiteboard_elements:
        element = whiteboard_element.get('element') if whiteboard_element else None
        ignore = not element or (element.get('type') == 'i-text' and not element.get('text', '').strip())
        if ignore:
            continue
        queue_for_preview_image = True
        if WhiteboardElement.get_id_per_uuid(whiteboard_element.get('uuid')):
            upserted = _update_whiteboard_element(
                whiteboard_element=whiteboard_element,
                whiteboard_id=whiteboard_id,
            )
        else:
            z_indexes = [w.z_index for w in WhiteboardElement.find_by_whiteboard_id(whiteboard_id)]
            next_available_z_index = max(z_indexes) + 1 if z_indexes else 0
            upserted = _create_whiteboard_element(
                asset_id=whiteboard_element.get('assetId'),
                element=element,
                whiteboard_id=whiteboard_id,
                z_index=next_available_z_index,
            )
            next_available_z_index += 1
        results.append(upserted)
    if queue_for_preview_image:
        WhiteboardHousekeeping.queue_for_preview_image(whiteboard_id)
    if not app.config['TESTING']:
        logger.info(f'socketio: Emit upsert_whiteboard_elements where whiteboard_id = {whiteboard_id} AND socket_id = {socket_id}')
        emit(
            'upsert_whiteboard_elements',
            whiteboard_elements,
            include_self=False,
            namespace=SOCKET_IO_NAMESPACE,
            skip_sid=socket_id,
            to=get_socket_io_room(whiteboard_id),
        )
    WhiteboardSession.update_updated_at(
        socket_id=socket_id,
        user_id=current_user.user_id,
        whiteboard_id=whiteboard_id,
    )
    return results


def _filter_per_feature_flag(enums):
    feature_flag = app.config['FEATURE_FLAG_WHITEBOARDS']
    return enums if feature_flag else list(filter(lambda enum: 'whiteboard' not in enum, enums))


def _create_whiteboard_element(
    asset_id,
    element,
    whiteboard_id,
    z_index,
):
    _validate_fabricjs_element(element)
    whiteboard_element = WhiteboardElement.create(
        asset_id=asset_id,
        element=element,
        uuid=element['uuid'],
        whiteboard_id=whiteboard_id,
        z_index=z_index,
    )
    if asset_id:
        asset = Asset.find_by_id(asset_id)
        if asset:
            user_id = current_user.user_id
            if user_id not in [user.id for user in asset.users]:
                course_id = current_user.course.id
                whiteboard_activity = Activity.create(
                    activity_type='whiteboard_add_asset',
                    course_id=course_id,
                    user_id=user_id,
                    object_type='whiteboard',
                    object_id=whiteboard_id,
                    asset_id=asset.id,
                )
                for asset_user in asset.users:
                    Activity.create(
                        activity_type='get_whiteboard_add_asset',
                        course_id=course_id,
                        user_id=asset_user.id,
                        object_type='whiteboard',
                        object_id=whiteboard_id,
                        asset_id=asset.id,
                        actor_id=user_id,
                        reciprocal_id=whiteboard_activity.id,
                    )
    return whiteboard_element.to_api_json()


def _update_whiteboard_element(whiteboard_element, whiteboard_id):
    if not whiteboard_element:
        raise BadRequestError('Element required')

    element = whiteboard_element['element']
    _validate_fabricjs_element(element, True)

    result = WhiteboardElement.update(
        asset_id=whiteboard_element.get('assetId'),
        element=element,
        uuid=element['uuid'],
        whiteboard_id=whiteboard_id,
    )
    if result:
        return result.to_api_json()


def _validate_fabricjs_element(element, is_update=False):
    error_message = None
    if element['type'] == 'i-text' and not safe_strip(element.get('text')):
        error_message = f'Invalid Fabric i-text element: {element}.'
    if is_update:
        if 'uuid' not in element:
            error_message = 'uuid is required when updating existing whiteboard_element.'
    if error_message:
        app.logger.error(error_message)
        raise BadRequestError(error_message)
