BEGIN;

ALTER TABLE courses ADD COLUMN protects_assets_per_section boolean DEFAULT false NOT NULL;

COMMIT;
