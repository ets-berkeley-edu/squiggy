/**
 * Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.
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
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

--

CREATE TYPE enum_activities_object_type AS ENUM (
    'asset',
    'canvas_discussion',
    'canvas_submission',
    'comment',
    'whiteboard'
);

--

CREATE TYPE enum_activities_type AS ENUM (
    'asset_add',
    'asset_comment',
    'asset_like',
    'asset_view',
    'assignment_submit',
    'discussion_entry',
    'discussion_topic',
    'get_asset_comment',
    'get_asset_comment_reply',
    'get_asset_like',
    'get_asset_view',
    'get_discussion_entry_reply',
    'get_whiteboard_add_asset',
    'get_whiteboard_remix',
    'whiteboard_add_asset',
    'whiteboard_export',
    'whiteboard_remix'
);

--

CREATE TYPE enum_assets_type AS ENUM (
    'file',
    'link',
    'whiteboard'
);

--

CREATE TYPE enum_users_canvas_enrollment_state AS ENUM (
    'active',
    'completed',
    'inactive',
    'invited',
    'rejected'
);

--

CREATE TABLE activities (
    id integer NOT NULL,
    type enum_activities_type NOT NULL,
    object_id integer,
    object_type enum_activities_object_type NOT NULL,
    metadata json,
    asset_id integer,
    course_id integer NOT NULL,
    user_id integer NOT NULL,
    actor_id integer,
    reciprocal_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE activities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE activities_id_seq OWNED BY activities.id;
ALTER TABLE ONLY activities ALTER COLUMN id SET DEFAULT nextval('activities_id_seq'::regclass);

ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);

CREATE INDEX activities_actor_id_idx ON activities USING btree (actor_id);
CREATE INDEX activities_asset_id_idx ON activities USING btree (asset_id);
CREATE INDEX activities_created_at_idx ON activities USING btree (created_at);

--

CREATE TABLE activity_types (
    id integer NOT NULL,
    type enum_activities_type NOT NULL,
    points integer,
    enabled boolean DEFAULT true,
    course_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE activity_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE activity_types_id_seq OWNED BY activity_types.id;
ALTER TABLE ONLY activity_types ALTER COLUMN id SET DEFAULT nextval('activity_types_id_seq'::regclass);

ALTER TABLE ONLY activity_types
    ADD CONSTRAINT activity_types_pkey PRIMARY KEY (id, course_id);

CREATE UNIQUE INDEX activity_types_type_course_id_idx ON activity_types USING btree (type, course_id);

--

CREATE TABLE asset_categories (
    asset_id integer NOT NULL,
    category_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY asset_categories
    ADD CONSTRAINT asset_categories_pkey PRIMARY KEY (asset_id, category_id);

CREATE INDEX asset_categories_asset_id_idx ON asset_categories USING btree (asset_id);
CREATE INDEX asset_categories_category_id_idx ON asset_categories USING btree (category_id);

--

CREATE TABLE asset_users (
    asset_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY asset_users
    ADD CONSTRAINT asset_users_pkey PRIMARY KEY (asset_id, user_id);

CREATE INDEX asset_users_asset_id_idx ON asset_users USING btree (asset_id);
CREATE INDEX asset_users_user_id_idx ON asset_users USING btree (user_id);

--

CREATE TABLE asset_whiteboard_elements (
    uuid character varying(255) NOT NULL,
    element json NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    asset_id integer NOT NULL,
    element_asset_id integer,
    z_index integer NOT NULL
);

ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_pkey PRIMARY KEY (uuid, asset_id, created_at);

--

CREATE TABLE assets (
    id integer NOT NULL,
    body text,
    canvas_assignment_id integer,
    comment_count integer DEFAULT 0,
    course_id integer NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    description text,
    dislikes integer DEFAULT 0,
    download_url text,
    image_url text,
    likes integer DEFAULT 0,
    mime character varying(255),
    pdf_url text,
    preview_metadata json DEFAULT '"{}"'::json,
    preview_status character varying(255) DEFAULT 'pending'::character varying,
    source character varying(255),
    thumbnail_url text,
    title character varying(255),
    type enum_assets_type NOT NULL,
    url text,
    views integer DEFAULT 0,
    visible boolean DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE assets_id_seq OWNED BY assets.id;
ALTER TABLE ONLY assets ALTER COLUMN id SET DEFAULT nextval('assets_id_seq'::regclass);

ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);

--

CREATE TABLE canvas (
    canvas_api_domain character varying(255) NOT NULL,
    api_key character varying(255) NOT NULL,
    lti_key character varying(255) NOT NULL,
    lti_secret character varying(255) NOT NULL,
    name character varying(255),
    supports_custom_messaging boolean DEFAULT false NOT NULL,
    use_https boolean DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_pkey PRIMARY KEY (canvas_api_domain);
ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_lti_key_key UNIQUE (lti_key);
ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_lti_secret_key UNIQUE (lti_secret);

--

CREATE TABLE canvas_poller_api_keys (
    canvas_api_domain character varying(255) NOT NULL,
    api_key character varying(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY canvas_poller_api_keys
    ADD CONSTRAINT canvas_poller_api_keys_pkey PRIMARY KEY (canvas_api_domain, api_key);

--

CREATE TABLE categories (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    canvas_assignment_id integer,
    canvas_assignment_name character varying(255),
    course_id integer,
    deleted_at timestamp with time zone,
    visible boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


CREATE SEQUENCE categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE categories_id_seq OWNED BY categories.id;
ALTER TABLE ONLY categories ALTER COLUMN id SET DEFAULT nextval('categories_id_seq'::regclass);

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);

--

CREATE TABLE comments (
    id integer NOT NULL,
    body text NOT NULL,
    asset_id integer NOT NULL,
    user_id integer,
    parent_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE comments_id_seq OWNED BY comments.id;
ALTER TABLE ONLY comments ALTER COLUMN id SET DEFAULT nextval('comments_id_seq'::regclass);

ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);

--

CREATE TABLE course_groups (
    id integer NOT NULL,
    course_id integer NOT NULL,
    canvas_group_id integer NOT NULL,
    name character varying(255),
    category_name character varying(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE course_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE course_groups_id_seq OWNED BY course_groups.id;
ALTER TABLE ONLY course_groups ALTER COLUMN id SET DEFAULT nextval('course_groups_id_seq'::regclass);

ALTER TABLE ONLY course_groups
    ADD CONSTRAINT course_groups_pkey PRIMARY KEY (id);

--

CREATE TABLE course_group_memberships (
    course_id integer NOT NULL,
    course_group_id integer NOT NULL,
    canvas_user_id integer NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY course_group_memberships
    ADD CONSTRAINT course_group_memberships_pkey PRIMARY KEY (course_group_id, canvas_user_id);

CREATE INDEX course_group_memberships_canvas_user_id_idx ON course_group_memberships USING btree (canvas_user_id);

--

CREATE TABLE courses (
    id integer NOT NULL,
    active boolean DEFAULT true NOT NULL,
    asset_library_url character varying(255),
    canvas_api_domain character varying(255) NOT NULL,
    canvas_course_id integer NOT NULL,
    enable_daily_notifications boolean DEFAULT true NOT NULL,
    enable_upload boolean DEFAULT true NOT NULL,
    enable_weekly_notifications boolean DEFAULT true NOT NULL,
    engagement_index_url character varying(255),
    name character varying(255),
    last_polled TIMESTAMP WITH TIME ZONE,
    whiteboards_url character varying(255),
    impact_studio_url character varying(255),
    protects_assets_per_section boolean DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE courses_id_seq OWNED BY courses.id;
ALTER TABLE ONLY courses ALTER COLUMN id SET DEFAULT nextval('courses_id_seq'::regclass);

ALTER TABLE ONLY courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);

CREATE INDEX courses_last_polled_idx ON courses USING btree (last_polled);

--

CREATE TABLE users (
    id integer NOT NULL,
    bookmarklet_token character varying(32) NOT NULL,
    canvas_user_id integer NOT NULL,
    canvas_course_role character varying(255) NOT NULL,
    canvas_enrollment_state enum_users_canvas_enrollment_state NOT NULL,
    canvas_full_name character varying(255) NOT NULL,
    canvas_image character varying(255),
    canvas_email character varying(255),
    personal_description character varying(255),
    points integer DEFAULT 0 NOT NULL,
    course_id integer NOT NULL,
    share_points boolean,
    looking_for_collaborators boolean DEFAULT false NOT NULL,
    last_activity timestamp with time zone,
    canvas_course_sections character varying(255)[],
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE users_id_seq OWNED BY users.id;
ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

--

CREATE TABLE whiteboard_elements (
    id integer NOT NULL,
    uuid character varying(255) NOT NULL,
    element json NOT NULL,
    whiteboard_id integer NOT NULL,
    asset_id integer,
    z_index integer NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE whiteboard_elements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE whiteboard_elements_id_seq OWNED BY whiteboard_elements.id;
ALTER TABLE ONLY whiteboard_elements ALTER COLUMN id SET DEFAULT nextval('whiteboard_elements_id_seq'::regclass);

CREATE UNIQUE INDEX whiteboard_elements_created_at_uuid_whiteboard_id_idx ON whiteboard_elements USING btree (uuid, whiteboard_id, created_at);

--

CREATE TABLE whiteboard_sessions (
    socket_id character varying(255) NOT NULL,
    whiteboard_id integer NOT NULL,
    user_id integer NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY whiteboard_sessions
    ADD CONSTRAINT whiteboard_sessions_pkey PRIMARY KEY (socket_id);

--

CREATE TABLE whiteboard_users (
    user_id integer NOT NULL,
    whiteboard_id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY whiteboard_users
    ADD CONSTRAINT whiteboard_users_pkey PRIMARY KEY (user_id, whiteboard_id);

CREATE INDEX whiteboard_users_whiteboard_id_idx ON whiteboard_users USING btree (whiteboard_id);
CREATE INDEX whiteboard_users_user_id_idx ON whiteboard_users USING btree (user_id);

--

CREATE TABLE whiteboards (
    id integer NOT NULL,
    course_id integer NOT NULL,
    image_url character varying(255),
    thumbnail_url character varying(255),
    title character varying(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE whiteboards_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE whiteboards_id_seq OWNED BY whiteboards.id;
ALTER TABLE ONLY whiteboards ALTER COLUMN id SET DEFAULT nextval('whiteboards_id_seq'::regclass);

ALTER TABLE ONLY whiteboards
    ADD CONSTRAINT whiteboards_pkey PRIMARY KEY (id);

--

ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_reciprocal_id_fkey FOREIGN KEY (reciprocal_id) REFERENCES activities(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY activity_types
    ADD CONSTRAINT activity_types_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_categories
    ADD CONSTRAINT asset_categories_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_categories
    ADD CONSTRAINT asset_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES categories(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_users
    ADD CONSTRAINT asset_users_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_users
    ADD CONSTRAINT asset_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_element_asset_id_fkey FOREIGN KEY (element_asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY canvas_poller_api_keys
    ADD CONSTRAINT canvas_poller_api_keys_canvas_api_domain_fkey FOREIGN KEY (canvas_api_domain) REFERENCES canvas(canvas_api_domain) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES comments(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY course_group_memberships
    ADD CONSTRAINT course_group_memberships_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY course_group_memberships
    ADD CONSTRAINT course_group_memberships_course_group_id_fkey FOREIGN KEY (course_group_id) REFERENCES course_groups(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY course_groups
    ADD CONSTRAINT course_groups_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE ONLY courses
    ADD CONSTRAINT courses_canvas_api_domain_fkey FOREIGN KEY (canvas_api_domain) REFERENCES canvas(canvas_api_domain) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY users
    ADD CONSTRAINT users_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_elements
    ADD CONSTRAINT whiteboard_elements_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_elements
    ADD CONSTRAINT whiteboard_elements_whiteboard_id_fkey FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_sessions
    ADD CONSTRAINT whiteboard_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_sessions
    ADD CONSTRAINT whiteboard_sessions_whiteboard_id_fkey FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_users
    ADD CONSTRAINT whiteboard_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboard_users
    ADD CONSTRAINT whiteboard_users_whiteboard_id_fkey FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY whiteboards
    ADD CONSTRAINT whiteboards_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
