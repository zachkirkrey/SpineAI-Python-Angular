"""Unit tests for ingst_studies.py."""

import os

from pony import orm

from testutil import unittest

from lib import database_lib
from lib import schema
from runtime import study_reader


TEST_DICOM_FILES = os.path.join(unittest.PROJECT_PATH, 'testdata/dicom_ucla_BAAATUQQ/')


class ImgLibTest(unittest.TestCase):

    def test_ignores_duplicate_study(self):
        db = database_lib.SpineAIDatabase('memory')

        reader = study_reader.StudyReader()
        study = reader.ingest_study(TEST_DICOM_FILES)

        with orm.db_session:
            existing_studies = orm.select(s for s in schema.Study)[:]
            self.assertEqual(len(existing_studies), 1)

        study = reader.ingest_study(TEST_DICOM_FILES)
        self.assertIsNone(study)

        with orm.db_session:
            existing_studies = orm.select(s for s in schema.Study)[:]
            self.assertEqual(len(existing_studies), 1)



if __name__ == '__main__':
    unittest.main()
