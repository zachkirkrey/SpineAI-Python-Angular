"""Unit tests for series_lib.py"""

import os
import tempfile

import numpy
from pony import orm
import SimpleITK

from testutil import unittest

from lib import dicom_lib
from lib import series_lib

from lib import schema

TEST_DICOM_FILES = os.path.join(unittest.PROJECT_PATH, 'testdata/dicom_ucla_BAAATUQQ/**/*')


class SeriesTest(unittest.TestCase):

    @orm.db_session
    def testGetImagePosition(self):
        series = schema.ImageSeries[5]
        self.assertListEqual(
                series.get_image_position(0),
                [-105.51000779936, -73.125646948815, -308.35692338181])


    @orm.db_session
    def testGetPatientCoordinates(self):
        series = schema.ImageSeries[5]
        numpy.testing.assert_allclose(
                series.get_patient_coordinates((0, 0, 0)),
                numpy.asarray([-105.5100078,
                               -73.12564695,
                               -308.35692338]))

    @orm.db_session
    def testGetPixelCoordinates(self):
        series = schema.ImageSeries[5]
        numpy.testing.assert_array_equal(
                series.get_pixel_coordinates([-105.5100078,
                                            -73.12564695,
                                            -308.35692338]),
                numpy.asarray([0, 0, 0]))

    @orm.db_session
    def testCoordinatesReversible(self):
        series = schema.ImageSeries[5]
        numpy.testing.assert_array_equal(
                series.get_pixel_coordinates(
                    series.get_patient_coordinates((12, 16, 22))),
                (12, 16, 22))

if __name__ == '__main__':
    unittest.main()
