"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, AND distribute this software AND its documentation
for educational, research, AND not-for-profit purposes, without fee AND without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph AND the following two paragraphs appear in all copies,
modifications, AND distributions.

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
import inspect

from flask import current_app as app


def get_prod_data_importer_sql(table_name):
    sql_factory_methods = {
        'activities': get_activities_sql,
        'activity_types': get_activity_types_sql,
        'asset_categories': get_asset_categories_sql,
        'asset_users': get_asset_users_sql,
        'asset_whiteboard_elements': get_asset_whiteboard_elements_sql,
        'assets': get_assets_sql,
        'categories': get_categories_sql,
        'comments': get_comments_sql,
        'courses': get_courses_sql,
        'users': get_users_sql,
        'whiteboard_elements': get_whiteboard_elements_sql,
        'whiteboard_members': get_whiteboard_members_sql,
        'whiteboards': get_whiteboards_sql,
    }
    method = sql_factory_methods[table_name]
    method_args = inspect.getfullargspec(method).args
    canvas_api_domain = app.config['PROD_DATA_IMPORTER_CANVAS_API_DOMAIN']
    if len(method_args) == 2:
        canvas_api_domain_repoint = app.config['PROD_DATA_IMPORTER_CANVAS_API_DOMAIN_REPOINT']
        sql = method(canvas_api_domain=canvas_api_domain, canvas_api_domain_repoint=canvas_api_domain_repoint)
    else:
        sql = method(canvas_api_domain=canvas_api_domain)
    return sql


def get_activities_sql(canvas_api_domain=None):
    join = _join_condition(canvas_api_domain=canvas_api_domain)
    return f'SELECT t.* FROM activities t {join} ORDER BY t.id'


def get_activity_types_sql(canvas_api_domain=None):
    join = _join_condition(canvas_api_domain=canvas_api_domain)
    return f'SELECT t.* FROM activity_types t {join}'


def get_assets_sql(canvas_api_domain=None):
    join = _join_condition(canvas_api_domain=canvas_api_domain)
    return f'SELECT t.* FROM assets t {join}'


def get_asset_users_sql(canvas_api_domain=None):
    join = _join_condition(canvas_api_domain=canvas_api_domain)
    return f'SELECT u.* FROM asset_users u JOIN (users t {join}) ON u.user_id = t.id'


def get_asset_categories_sql(canvas_api_domain=None):
    sql = 'SELECT a.* FROM assets_categories a'
    if canvas_api_domain:
        join = _join_condition(canvas_api_domain=canvas_api_domain)
        sql += f' JOIN (categories t {join}) ON a.category_id = t.id'
    return sql


def get_asset_whiteboard_elements_sql(canvas_api_domain=None):
    join = _join_condition(canvas_api_domain=canvas_api_domain)
    return f"""
      SELECT awe.*
      FROM asset_whiteboard_elements awe
      JOIN (assets t {join}) ON awe.asset_id = t.id
    """


def get_categories_sql(canvas_api_domain=None):
    return f"""
        SELECT cat.*
        FROM categories cat
        JOIN courses c ON cat.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def get_comments_sql(canvas_api_domain=None):
    return f"""
        SELECT com.*
        FROM comments com
        JOIN (
            users u JOIN courses c ON u.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON com.user_id = u.id
    """


def get_courses_sql(canvas_api_domain=None, canvas_api_domain_repoint=None):
    return f"""
        SELECT
            c.id, c.canvas_course_id, c.enable_upload, c.name,
            REPLACE(c.assetlibrary_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS assetlibrary_url,
            REPLACE(c.dashboard_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS dashboard_url,
            REPLACE(c.engagementindex_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS engagementindex_url,
            REPLACE(c.whiteboards_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS whiteboards_url,
            '{canvas_api_domain_repoint}' AS canvas_api_domain,
            c.active, c.created_at, c.updated_at, c.enable_daily_notifications, c.enable_weekly_notifications
        FROM courses c
        WHERE c.canvas_api_domain = '{canvas_api_domain}'
    """


def get_users_sql(canvas_api_domain=None):
    return f"""
        SELECT u.*
        FROM users u
        JOIN courses c ON u.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def get_whiteboard_elements_sql(canvas_api_domain=None, canvas_api_domain_repoint=None):
    return f"""
        SELECT
            we.uid,
            REPLACE(we.element::text, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS element,
            we.created_at, we.updated_at, we.whiteboard_id, we.asset_id
        FROM whiteboard_elements we
        JOIN (
            whiteboards w join courses c on w.course_id = c.id and c.canvas_api_domain = '{canvas_api_domain}'
        ) ON we.whiteboard_id = w.id
    """


def get_whiteboard_members_sql(canvas_api_domain=None):
    return f"""
        SELECT wm.* FROM whiteboard_members wm
        JOIN (
            whiteboards w
            JOIN courses c ON w.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON wm.whiteboard_id = w.id
    """


def get_whiteboards_sql(canvas_api_domain=None, canvas_api_domain_repoint=None):
    return f"""
        SELECT
            w.id, w.title,
            replace(w.thumbnail_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS thumbnail_url,
            replace(w.image_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS image_url,
            w.created_at, w.updated_at, w.course_id, w.deleted_at
        FROM whiteboards w
        JOIN courses c ON w.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def _join_condition(canvas_api_domain):
    return f"""
      JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """ if canvas_api_domain else ''
