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
        'activities': _get_activities_sql,
        'activity_types': _get_activity_types_sql,
        'asset_categories': _get_asset_categories_sql,
        'asset_users': _get_asset_users_sql,
        'asset_whiteboard_elements': _get_asset_whiteboard_elements_sql,
        'assets': _get_assets_sql,
        'categories': _get_categories_sql,
        'comments': _get_comments_sql,
        'courses': _get_courses_sql,
        'users': _get_users_sql,
        'whiteboard_elements': _get_whiteboard_elements_sql,
        'whiteboard_users': _get_whiteboard_users_sql,
        'whiteboards': _get_whiteboards_sql,
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


def _get_activities_sql(canvas_api_domain):
    return f"""
        SELECT t.*
        FROM activities t
        JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ORDER BY t.id
    """


def _get_activity_types_sql(canvas_api_domain):
    return f"""
        SELECT t.*
        FROM activity_types t
        JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def _get_asset_categories_sql(canvas_api_domain):
    return f"""
        SELECT a.*
        FROM asset_categories a
        JOIN (
            categories t JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON a.category_id = t.id
    """


def _get_asset_users_sql(canvas_api_domain):
    return f"""
        SELECT u.*
        FROM asset_users u
        JOIN (
            users t JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON u.user_id = t.id
    """


def _get_asset_whiteboard_elements_sql(canvas_api_domain):
    return f"""
      SELECT awe.*
      FROM asset_whiteboard_elements awe
      JOIN (
          assets t JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
      ) ON awe.asset_id = t.id
    """


def _get_assets_sql(canvas_api_domain):
    return f"""
        SELECT t.*
        FROM assets t
        JOIN courses c ON t.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def _get_categories_sql(canvas_api_domain):
    return f"""
        SELECT cat.*
        FROM categories cat
        JOIN courses c ON cat.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def _get_comments_sql(canvas_api_domain):
    return f"""
        SELECT com.*
        FROM comments com
        JOIN (
            users u JOIN courses c ON u.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON com.user_id = u.id
    """


def _get_courses_sql(canvas_api_domain, canvas_api_domain_repoint):
    return f"""
        SELECT
            c.id, c.canvas_course_id, c.enable_upload, c.name,
            REPLACE(c.asset_library_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS asset_library_url,
            REPLACE(c.impact_studio_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS impact_studio_url,
            REPLACE(c.engagement_index_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS engagement_index_url,
            REPLACE(c.whiteboards_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS whiteboards_url,
            '{canvas_api_domain_repoint}' AS canvas_api_domain,
            c.active, c.created_at, c.updated_at, c.enable_daily_notifications, c.enable_weekly_notifications
        FROM courses c
        WHERE c.canvas_api_domain = '{canvas_api_domain}'
    """


def _get_users_sql(canvas_api_domain):
    return f"""
        SELECT u.*
        FROM users u
        JOIN courses c ON u.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """


def _get_whiteboard_elements_sql(canvas_api_domain, canvas_api_domain_repoint):
    return f"""
        SELECT
            we.uuid,
            REPLACE(we.element::text, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS element,
            we.created_at, we.updated_at, we.whiteboard_id, we.asset_id
        FROM whiteboard_elements we
        JOIN (
            whiteboards w join courses c on w.course_id = c.id and c.canvas_api_domain = '{canvas_api_domain}'
        ) ON we.whiteboard_id = w.id
    """


def _get_whiteboard_users_sql(canvas_api_domain):
    return f"""
        SELECT wm.* FROM whiteboard_users wm
        JOIN (
            whiteboards w
            JOIN courses c ON w.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
        ) ON wm.whiteboard_id = w.id
    """


def _get_whiteboards_sql(canvas_api_domain, canvas_api_domain_repoint):
    return f"""
        SELECT
            w.id, w.title,
            replace(w.thumbnail_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS thumbnail_url,
            replace(w.image_url, '{canvas_api_domain}', '{canvas_api_domain_repoint}') AS image_url,
            w.created_at, w.updated_at, w.course_id, w.deleted_at
        FROM whiteboards w
        JOIN courses c ON w.course_id = c.id AND c.canvas_api_domain = '{canvas_api_domain}'
    """
