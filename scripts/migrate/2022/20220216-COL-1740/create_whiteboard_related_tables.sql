BEGIN;

CREATE TABLE asset_whiteboard_elements (
    asset_id integer NOT NULL,
    element json NOT NULL,
    element_asset_id integer,
    uid text NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_pkey PRIMARY KEY (uid, asset_id);

--

CREATE TABLE whiteboard_elements (
    uid integer NOT NULL,
    element json NOT NULL,
    whiteboard_id integer NOT NULL,
    asset_id integer,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY whiteboard_elements
    ADD CONSTRAINT whiteboard_elements_pkey PRIMARY KEY (uid, whiteboard_id);

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

ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY asset_whiteboard_elements
    ADD CONSTRAINT asset_whiteboard_elements_element_asset_id_fkey FOREIGN KEY (element_asset_id) REFERENCES assets(id) ON UPDATE CASCADE ON DELETE CASCADE;

--

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

--

COMMIT;
