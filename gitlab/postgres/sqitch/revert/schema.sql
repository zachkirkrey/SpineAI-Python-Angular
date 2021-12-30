-- Revert spineai-gitlab:appschema from pg

BEGIN;

-- XXX Add DDLs here.
DROP SCHEMA qa;

COMMIT;
