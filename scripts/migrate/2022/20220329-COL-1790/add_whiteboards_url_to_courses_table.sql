BEGIN;

ALTER TABLE courses ADD COLUMN whiteboards_url character varying(255);

COMMIT;
