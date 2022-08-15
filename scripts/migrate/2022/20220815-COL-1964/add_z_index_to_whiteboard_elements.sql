BEGIN;

ALTER TABLE asset_whiteboard_elements ADD COLUMN IF NOT EXISTS z_index INTEGER;
ALTER TABLE whiteboard_elements ADD COLUMN IF NOT EXISTS z_index INTEGER;

UPDATE asset_whiteboard_elements u SET z_index = 0;
UPDATE whiteboard_elements u SET z_index = 0;

ALTER TABLE ONLY asset_whiteboard_elements ALTER COLUMN z_index SET NOT NULL;
ALTER TABLE ONLY whiteboard_elements ALTER COLUMN z_index SET NOT NULL;

COMMIT;
