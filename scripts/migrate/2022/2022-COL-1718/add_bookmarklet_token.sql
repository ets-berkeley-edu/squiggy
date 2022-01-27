BEGIN;

ALTER TABLE users ADD COLUMN IF NOT EXISTS bookmarklet_token VARCHAR(32);

UPDATE users u SET bookmarklet_token = MD5(random()::text);

-- Column is not nullable.
ALTER TABLE ONLY users ALTER COLUMN bookmarklet_token SET NOT NULL;

COMMIT;
