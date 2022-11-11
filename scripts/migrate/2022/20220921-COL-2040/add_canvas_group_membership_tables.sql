BEGIN;

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

ALTER TABLE ONLY course_group_memberships
    ADD CONSTRAINT course_group_memberships_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY course_group_memberships
    ADD CONSTRAINT course_group_memberships_course_group_id_fkey FOREIGN KEY (course_group_id) REFERENCES course_groups(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY course_groups
    ADD CONSTRAINT course_groups_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE;

COMMIT;
