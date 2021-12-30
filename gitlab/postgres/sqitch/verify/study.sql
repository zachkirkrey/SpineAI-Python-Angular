-- Verify spineai-gitlab:studies on pg

BEGIN;

-- XXX Add verifications here.
SELECT name, study_type, study_source
FROM qa.study
WHERE false;


ROLLBACK;
