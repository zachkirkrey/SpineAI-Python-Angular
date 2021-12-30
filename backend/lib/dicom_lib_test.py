"""Unit tests for dicom_lib.py"""

import os

from testutil import unittest

from lib import study_lib
from lib import dicom_lib
from lib import series_lib

TEST_DICOM_FILES = os.path.join(unittest.PROJECT_PATH, 'testdata/dicom_ucla_BAAATUQQ/1.3.12.2.1107.5.2.30.27595.2013030313205668539705283.0.0.0')

class DicomLibTest(unittest.TestCase):
    pass

    # def test_get_orientation(self):
    #     series = series_lib.PatientSeriesFromDICOMFiles(TEST_DICOM_FILES)[0]
    #     orientation = dicom_lib.get_orientation(series)
    #     self.assertEqual(orientation, dicom_lib.Orientation.CORONAL)


if __name__ == '__main__':
    unittest.main()
