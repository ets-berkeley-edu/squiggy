BEGIN;

ALTER TABLE courses ADD COLUMN impact_studio_url character varying(255);

ALTER TABLE users ADD COLUMN personal_description character varying(255);
ALTER TABLE users ADD COLUMN looking_for_collaborators boolean DEFAULT false NOT NULL;

COMMIT;
