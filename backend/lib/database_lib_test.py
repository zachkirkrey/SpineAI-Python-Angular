"""Unit tests for database_lib.py"""

import os

from pony import orm

from testutil import unittest

from lib import database_lib
from lib import schema
from runtime import study_reader


TEST_DICOM_FILES = os.path.join(unittest.PROJECT_PATH, 'testdata/dicom_ucla_BAABQXXR')


class DatabaseLibTest(unittest.TestCase):
    pass



if __name__ == '__main__':
    unittest.main()
