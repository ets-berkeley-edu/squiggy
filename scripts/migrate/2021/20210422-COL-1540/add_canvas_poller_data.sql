BEGIN;

CREATE TABLE canvas_poller_api_keys (
    canvas_api_domain character varying(255) NOT NULL,
    api_key character varying(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

ALTER TABLE ONLY canvas_poller_api_keys
    ADD CONSTRAINT canvas_poller_api_keys_pkey PRIMARY KEY (canvas_api_domain, api_key);

ALTER TABLE ONLY canvas_poller_api_keys
    ADD CONSTRAINT canvas_poller_api_keys_canvas_api_domain_fkey FOREIGN KEY (canvas_api_domain) REFERENCES canvas(canvas_api_domain) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY courses
    ADD COLUMN last_polled TIMESTAMP WITH TIME ZONE;

CREATE INDEX courses_last_polled_idx ON courses USING btree (last_polled);

COMMIT;
