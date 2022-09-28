BEGIN;

ALTER TABLE assets ADD COLUMN created_by integer;
UPDATE assets a SET created_by = COALESCE((
    SELECT user_id
    FROM asset_users au
    WHERE au.asset_id = a.id
    ORDER BY au.created_at
    LIMIT 1
), 0);
ALTER TABLE ONLY assets ALTER COLUMN created_by SET NOT NULL;

ALTER TABLE whiteboards ADD COLUMN created_by integer;
UPDATE whiteboards w SET created_by = COALESCE((
    SELECT user_id
    FROM whiteboard_users wu
    WHERE wu.whiteboard_id = w.id
    ORDER BY wu.created_at
    LIMIT 1
), 0);
ALTER TABLE ONLY whiteboards ALTER COLUMN created_by SET NOT NULL;

COMMIT;
