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
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;

--

CREATE TYPE enum_assets_type AS ENUM (
    'file',
    'link',
    'thought'
);

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
    download_url character varying(255),
    image_url character varying(255),
    impact_percentile integer DEFAULT 0 NOT NULL,
    impact_score integer DEFAULT 0 NOT NULL,
    likes integer DEFAULT 0,
    mime character varying(255),
    pdf_url character varying(255),
    preview_metadata json DEFAULT '"{}"'::json,
    preview_status character varying(255) DEFAULT 'pending'::character varying,
    source character varying(255),
    thumbnail_url character varying(255),
    title character varying(255),
    trending_percentile integer DEFAULT 0 NOT NULL,
    trending_score integer DEFAULT 0 NOT NULL,
    type enum_assets_type NOT NULL,
    url character varying(255),
    views integer DEFAULT 0,
    visible boolean DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE assets OWNER TO squiggy;
CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE assets_id_seq OWNER TO squiggy;
ALTER SEQUENCE assets_id_seq OWNED BY assets.id;
ALTER TABLE ONLY assets ALTER COLUMN id SET DEFAULT nextval('assets_id_seq'::regclass);
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);

--

CREATE TABLE authorized_users (
    id integer NOT NULL,
    uid character varying(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE authorized_users OWNER TO squiggy;
CREATE SEQUENCE authorized_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE authorized_users_id_seq OWNER TO squiggy;
ALTER SEQUENCE authorized_users_id_seq OWNED BY authorized_users.id;
ALTER TABLE ONLY authorized_users ALTER COLUMN id SET DEFAULT nextval('authorized_users_id_seq'::regclass);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY authorized_users
    ADD CONSTRAINT authorized_users_uid_key UNIQUE (uid);

--

CREATE TABLE canvas (
    canvas_api_domain character varying(255) NOT NULL,
    api_key character varying(255) NOT NULL,
    logo character varying(255),
    lti_key character varying(255) NOT NULL,
    lti_secret character varying(255) NOT NULL,
    name character varying(255),
    supports_custom_messaging boolean DEFAULT false NOT NULL,
    use_https boolean DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
ALTER TABLE canvas OWNER TO squiggy;
ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_pkey PRIMARY KEY (canvas_api_domain);
ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_lti_key_key UNIQUE (lti_key);
ALTER TABLE ONLY canvas
    ADD CONSTRAINT canvas_lti_secret_key UNIQUE (lti_secret);

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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
ALTER TABLE courses OWNER TO squiggy;
CREATE SEQUENCE courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE courses_id_seq OWNER TO squiggy;
ALTER SEQUENCE courses_id_seq OWNED BY courses.id;
ALTER TABLE ONLY courses ALTER COLUMN id SET DEFAULT nextval('courses_id_seq'::regclass);
ALTER TABLE ONLY courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);

--

ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY courses
    ADD CONSTRAINT courses_canvas_api_domain_fkey FOREIGN KEY (canvas_api_domain) REFERENCES canvas(canvas_api_domain) ON UPDATE CASCADE ON DELETE CASCADE;
