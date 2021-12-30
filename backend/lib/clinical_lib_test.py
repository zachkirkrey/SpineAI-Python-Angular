"""Unit tests for clinical_lib.py"""

from pony import orm

from testutil import unittest

from lib import clinical_lib

from lib import schema


class CanalNarrowingMeasurement(unittest.TestCase):

    @orm.db_session
    def test_get_measurements(self):
        segmentation = schema.Segmentation.select(
                lambda s: s.type == schema.SegmentationType.CANAL.name)[:][0]

        measurements = clinical_lib.CanalNarrowingMeasurement(
                segmentation.canal_segmentation)
        self.assertTrue(measurements.get_measurements())


class CutlineMeasurement(unittest.TestCase):

    @orm.db_session
    def test_get_measurements(self):
        foramen_segmentation = schema.Segmentation.select(
                lambda s: s.type == schema.SegmentationType.FORAMEN.name)[:][0]
        sagittal_series = foramen_segmentation.postprocessed_segmentation_series

        canal_segmentation = schema.Segmentation.select(
                lambda s: s.type == schema.SegmentationType.CANAL.name)[:][0]
        axial_series = canal_segmentation.postprocessed_segmentation_series

        measurements = clinical_lib.CutlineMeasurement(
                sagittal_series, axial_series)
        self.assertTrue(measurements.get_measurements())


class GeisingerMeasurementTest(unittest.TestCase):

    @orm.db_session
    def test_get_measurements(self):
        segmentation = schema.Segmentation.select(
                lambda s: s.type == schema.SegmentationType.CANAL.name)[:][0]

        measurements = clinical_lib.GeisingerMeasurement(
                segmentation.canal_segmentation)
        self.assertTrue(measurements.get_measurements())


if __name__ == '__main__':
    unittest.main()
