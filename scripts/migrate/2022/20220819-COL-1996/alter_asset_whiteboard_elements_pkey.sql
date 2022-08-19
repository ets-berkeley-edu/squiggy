BEGIN;
ALTER TABLE asset_whiteboard_elements DROP CONSTRAINT asset_whiteboard_elements_pkey;
ALTER TABLE asset_whiteboard_elements ADD CONSTRAINT asset_whiteboard_elements_pkey PRIMARY KEY (asset_id, uuid, created_at);
COMMIT;
