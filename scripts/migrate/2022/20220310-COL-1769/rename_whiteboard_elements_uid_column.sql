BEGIN;

ALTER TABLE asset_whiteboard_elements DROP CONSTRAINT asset_whiteboard_elements_pkey;
ALTER TABLE asset_whiteboard_elements RENAME COLUMN uid TO uuid;
ALTER TABLE ONLY asset_whiteboard_elements
  ADD CONSTRAINT asset_whiteboard_elements_pkey PRIMARY KEY (uuid, asset_id);

DROP INDEX IF EXISTS whiteboard_elements_created_at_uid_whiteboard_id_idx;
ALTER TABLE whiteboard_elements RENAME COLUMN uid TO uuid;
CREATE UNIQUE INDEX whiteboard_elements_created_at_uuid_whiteboard_id_idx
  ON whiteboard_elements USING btree (uuid, whiteboard_id, created_at);

COMMIT;
