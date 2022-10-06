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

import sqlvalidator
from squiggy.lib.prod_data_importer_sql_factory import get_prod_data_importer_sql
from tests.util import override_config


def assert_sql(app, table_name, include_canvas_api_domain=False):
    canvas_api_domain = 'bcourses.berkeley.edu'
    canvas_api_domain_repoint = 'https://ucberkeley.beta.instructure.com'
    with override_config(app, 'PROD_DATA_IMPORTER_CANVAS_API_DOMAIN', canvas_api_domain):
        with override_config(app, 'PROD_DATA_IMPORTER_CANVAS_API_DOMAIN_REPOINT', canvas_api_domain_repoint):
            sql = get_prod_data_importer_sql(table_name)
            assert sqlvalidator.parse(sql).is_valid()


class TestSqlGeneration:
    """SQL generation."""

    def test_get_activities_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='activities',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_activity_types_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='activity_types',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_assets_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='assets',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_asset_users_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='asset_users',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_asset_categories_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='asset_categories',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_asset_whiteboard_elements_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='whiteboard_elements',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_categories_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='categories',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_comments_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='comments',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_courses_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='courses',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_users_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='users',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_whiteboard_elements_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='whiteboard_elements',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_whiteboard_users_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='whiteboard_users',
                include_canvas_api_domain=include_canvas_api_domain,
            )

    def test_get_whiteboards_sql(self, app):
        for include_canvas_api_domain in [False, True]:
            assert_sql(
                app,
                table_name='whiteboards',
                include_canvas_api_domain=include_canvas_api_domain,
            )
