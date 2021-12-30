"""Unittests for classifier_lib.py"""

import os

from PIL import Image
from pony import orm
import SimpleITK

from testutil import unittest

from lib import classifier_lib
from lib import dicom_lib
from lib import database_lib
from runtime import study_reader

from lib import schema

# class ClassificationTest(unittest.TestCase):
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#     # TODO(billy): Tests for to/from dir for Classification


class KerasImageClassifierTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with orm.db_session:
            self.test_study = schema.Study[1]

    @orm.db_session
    def test_sorted_by_fit(self):
        sorted_series = classifier_lib.KerasImageClassifier.sorted_by_fit(
                self.test_study.patient_series)

        # Uncomment this block to print actual series for new test data.
        # for series in sorted_series:
        #     print(series.is_t2())
        #     print(series.is_ir())
        #     print(series.image.GetDepth())

        # We expect to prioritize T2, non-IR, high depth series, in that order
        # of importance.
        expected_parameters = [{
            'is_t2': True,
            'is_ir': False,
            'depth': 42,
        }, {
            'is_t2': True,
            'is_ir': False,
            'depth': 13,
        }, {
            'is_t2': False,
            'is_ir': False,
            'depth': 42,
        }, {
            'is_t2': False,
            'is_ir': False,
            'depth': 35,
        }, {
            'is_t2': False,
            'is_ir': False,
            'depth': 13,
        }, {
            'is_t2': False,
            'is_ir': False,
            'depth': 13,
        }, {
            'is_t2': False,
            'is_ir': False,
            'depth': 12,
        }, {
            'is_t2': False,
            'is_ir': True,
            'depth': 13,
        }]
        for i, series in enumerate(sorted_series):
            self.assertEqual(series.is_t2(), expected_parameters[i]['is_t2'],
                    "Expected is_t2() == '{}' for series '{}'. Got: '{}'".format(
                        expected_parameters[i]['is_t2'], i, series.is_t2()))
            self.assertEqual(series.is_ir(), expected_parameters[i]['is_ir'],
                    "Expected is_ir() == '{}' for series '{}'. Got: '{}'".format(
                        expected_parameters[i]['is_ir'], i, series.is_ir()))
            self.assertEqual(
                    series.image.GetDepth(), expected_parameters[i]['depth'],
                    "Expected depth == '{}' for series '{}'. Got: '{}'".format(
                        expected_parameters[i]['depth'],
                        i,
                        series.image.GetDepth()))


# class DefaultCanalClassifierTest(unittest.TestCase):
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#     def test_init(self):
#         classifier = classifier_lib.DefaultCanalClassifier()
# 
#     # def test_sorted_by_fit(self):
#     #     sorted_series = classifier_lib.DefaultCanalClassifier.sorted_by_fit(
#     #             TEST_STUDY.patient_image_series)
# 
#     #     expected_orientations = [
#     #             dicom_lib.Orientation.AXIAL,
#     #             dicom_lib.Orientation.AXIAL,
#     #             dicom_lib.Orientation.AXIAL,
#     #             dicom_lib.Orientation.SAGITTAL_REVERSE,
#     #             dicom_lib.Orientation.SAGITTAL_REVERSE,
#     #             dicom_lib.Orientation.SAGITTAL_REVERSE,
#     #             dicom_lib.Orientation.SAGITTAL_REVERSE,
#     #             dicom_lib.Orientation.CORONAL]
#     #     for i, series in enumerate(sorted_series):
#     #         self.assertEqual(
#     #                 dicom_lib.get_orientation(series),
#     #                 expected_orientations[i],
#     #                 "Incorrect orientation for series #{}".format(i))

# class DefaultDiskClassifierTest(unittest.TestCase):
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#     def test_init(self):
#         classifier = classifier_lib.DefaultDiskClassifier()
# 
#     def test_sorted_by_fit(self):
#         pass
#         # TODO(billy): Fix after not flaky.
#         # sorted_series = classifier_lib.DefaultDiskClassifier.sorted_by_fit(
#         #         TEST_STUDY.patient_image_series)
# 
#         # expected_orientations = [
#         #         dicom_lib.Orientation.SAGITTAL_REVERSE,
#         #         dicom_lib.Orientation.SAGITTAL_REVERSE,
#         #         dicom_lib.Orientation.SAGITTAL_REVERSE,
#         #         dicom_lib.Orientation.SAGITTAL_REVERSE,
#         #         dicom_lib.Orientation.AXIAL,
#         #         dicom_lib.Orientation.AXIAL,
#         #         dicom_lib.Orientation.AXIAL,
#         #         dicom_lib.Orientation.CORONAL]
#         # for i, series in enumerate(sorted_series):
#         #     self.assertEqual(
#         #             dicom_lib.get_orientation(series),
#         #             expected_orientations[i],
#         #             "Incorrect orientation for series #{}".format(i))
# 
# 
# class DefaultForamenClassifierTest(unittest.TestCase):
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#     def test_init(self):
#         classifier = classifier_lib.DefaultForamenClassifier()

TEST_AXIAL_IMAGE = 'testdata/images/mendeley/axial/1.png'


class CanalXClassifierTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with orm.db_session:
            self.test_study = schema.Study[1]

        self.classifier = classifier_lib.DefaultCanalXClassifier()

    @orm.db_session
    def test_classify_slice(self):
        with Image.open(TEST_AXIAL_IMAGE) as axial_img:

            segmented = self.classifier.classify_slice(axial_img)

            tmp_output = '/tmp/xsegmented.png'
            segmented.save(tmp_output)

    @orm.db_session
    def test_classify(self):
        canal_classification = self.test_study.classifications.select(
                lambda c: c.type == schema.ClassificationType.CANAL.name)[:][0]

        self.classifier.classify(canal_classification, self.test_study)

if __name__ == '__main__':
    unittest.main()
