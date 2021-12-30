-- Revert spineai-gitlab:studies from pg

BEGIN;

-- XXX Add DDLs here.
DROP TABLE qa.study;
DROP TYPE qa.hash_type;
DROP TYPE qa.study_type;

COMMIT;
