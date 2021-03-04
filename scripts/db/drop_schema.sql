/**
 * Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--

ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_actor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_course_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_reciprocal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.activity_types DROP CONSTRAINT IF EXISTS activity_types_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_category_id_fkey;

ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.assets DROP CONSTRAINT IF EXISTS assets_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_course_id_fkey;

ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_asset_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_user_id_fkey;

ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_canvas_api_domain_fkey;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_course_id_fkey;

--

ALTER TABLE IF EXISTS ONLY public.activities DROP CONSTRAINT IF EXISTS activities_pkey;

ALTER TABLE IF EXISTS ONLY public.activity_types DROP CONSTRAINT IF EXISTS activity_types_pkey;

ALTER TABLE IF EXISTS ONLY public.asset_categories DROP CONSTRAINT IF EXISTS asset_categories_pkey;

ALTER TABLE IF EXISTS ONLY public.asset_users DROP CONSTRAINT IF EXISTS asset_users_pkey;

ALTER TABLE IF EXISTS ONLY public.assets DROP CONSTRAINT IF EXISTS assets_pkey;
ALTER TABLE IF EXISTS public.assets ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_pkey;
ALTER TABLE IF EXISTS ONLY public.authorized_users DROP CONSTRAINT IF EXISTS authorized_users_uid_key;
ALTER TABLE IF EXISTS public.authorized_users ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_lti_key_key;
ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_lti_secret_key;
ALTER TABLE IF EXISTS ONLY public.canvas DROP CONSTRAINT IF EXISTS canvas_pkey;

ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.comments DROP CONSTRAINT IF EXISTS comments_pkey;
ALTER TABLE IF EXISTS public.comments ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.courses DROP CONSTRAINT IF EXISTS courses_pkey;
ALTER TABLE IF EXISTS public.courses ALTER COLUMN id DROP DEFAULT;

ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;

--

DROP INDEX IF EXISTS activities_actor_id_idx;
DROP INDEX IF EXISTS activities_asset_id_idx;
DROP INDEX IF EXISTS activities_created_at_idx;

DROP INDEX IF EXISTS activity_types_type_course_id_idx;

DROP INDEX IF EXISTS asset_categories_asset_id_idx;
DROP INDEX IF EXISTS asset_categories_category_id_idx;

DROP INDEX IF EXISTS asset_users_asset_id_idx;
DROP INDEX IF EXISTS asset_users_user_id_idx;

--

DROP TABLE IF EXISTS public.activities;
DROP SEQUENCE IF EXISTS public.activities_id_seq;
DROP TABLE IF EXISTS public.activity_types;
DROP SEQUENCE IF EXISTS public.activity_types_id_seq;
DROP TABLE IF EXISTS public.asset_categories;
DROP TABLE IF EXISTS public.asset_users;
DROP SEQUENCE IF EXISTS public.assets_id_seq;
DROP TABLE IF EXISTS public.assets;
DROP SEQUENCE IF EXISTS public.authorized_users_id_seq;
DROP TABLE IF EXISTS public.authorized_users;
DROP TABLE IF EXISTS public.canvas;
DROP SEQUENCE IF EXISTS public.categories_id_seq;
DROP TABLE IF EXISTS public.categories;
DROP SEQUENCE IF EXISTS public.comments_id_seq;
DROP TABLE IF EXISTS public.comments;
DROP SEQUENCE IF EXISTS public.courses_id_seq;
DROP TABLE IF EXISTS public.courses;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;

--

DROP TYPE IF EXISTS public.enum_activities_object_type;
DROP TYPE IF EXISTS public.enum_activities_type;
DROP TYPE IF EXISTS public.enum_assets_type;
DROP TYPE IF EXISTS public.enum_users_canvas_enrollment_state;

--
