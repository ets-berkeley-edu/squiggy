BEGIN;

CREATE TABLE background_jobs (
    job_name character varying(255) NOT NULL,
    last_run TIMESTAMP WITH TIME ZONE
);

ALTER TABLE ONLY background_jobs
    ADD CONSTRAINT background_jobs_pkey PRIMARY KEY (job_name);

COMMIT;
