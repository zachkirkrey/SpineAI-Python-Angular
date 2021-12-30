-- Deploy spineai-gitlab:studies to pg
-- requires: schema

BEGIN;

-- XXX Add DDLs here.
SET client_min_messages = 'warning';

CREATE TYPE qa.hash_type AS ENUM (
  'CRC32');
CREATE TYPE qa.study_type AS ENUM (
  'DICOM_ZIP');

CREATE TABLE qa.study (
  id serial PRIMARY KEY,
  name text NOT NULL,
  creation_datetime timestamp NOT NULL default NOW(),

  hash_type qa.hash_type NOT NULL,
  hash_value bytea NOT NULL,

  study_type qa.study_type NOT NULL,
  study_source text NOT NULL,
  study_data bytea NOT NULL
);

COMMIT;
