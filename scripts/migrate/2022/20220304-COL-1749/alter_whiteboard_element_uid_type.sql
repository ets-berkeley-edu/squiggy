BEGIN;

ALTER TABLE asset_whiteboard_elements
    ALTER COLUMN uid SET DATA TYPE character varying(255);

ALTER TABLE whiteboard_elements
    ALTER COLUMN uid SET DATA TYPE character varying(255);

COMMIT;
