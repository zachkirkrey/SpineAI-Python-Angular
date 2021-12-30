"""Unit tests for img_lib.py."""

import os

import numpy
import SimpleITK

from testutil import unittest

from lib import img_lib
from lib import series_lib
from lib import study_lib


TEST_DICOM_FILES = os.path.join(unittest.PROJECT_PATH, 'testdata/dicom_ucla_BAAATUQQ/1.3.12.2.1107.5.2.30.27595.2013030313205668539705283.0.0.0')
SAGITTAL_HISTOGRAM_TEMPLATE = os.path.join(unittest.PROJECT_PATH, 'bin/histogram_templates/template_sagittal.nii.gz')


class ImgLibTest(unittest.TestCase):

    # This test takes > 2m so we skip it by default.
    #
    # TODO(billy): Create a system for optionally enabling large tests, or
    # optimize this test to run faster/on less slices.
    # def test_n4_bias_field_correction(self):
    #     series = series_lib.PatientSeriesFromDICOMFiles(TEST_DICOM_FILES)
    #     image = img_lib.n4_bias_field_correction(series[0].image)

    # def test_invert(self):
    #     series = series_lib.PatientSeriesFromDICOMFiles(TEST_DICOM_FILES)
    #     image = img_lib.invert(series[0].image)

    #     # TODO(billy): Invert validation.

    # def test_histomatch(self):
    #     series = series_lib.PatientSeriesFromDICOMFiles(TEST_DICOM_FILES)
    #     original_image = series[0].image

    #     template_image = SimpleITK.ReadImage(SAGITTAL_HISTOGRAM_TEMPLATE, original_image.GetPixelID())
    #     new_image = img_lib.histomatch(original_image, template_image)

    #     original_image_arr = SimpleITK.GetArrayFromImage(original_image)
    #     new_image_arr = SimpleITK.GetArrayFromImage(new_image)
    #     self.assertFalse(
    #             numpy.array_equal(original_image_arr, new_image_arr))

    def test_traverse_area_helper(self):
        array = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 1, 0]])

        actual_result = img_lib.traverse_area_helper(array, (0, 0))
        expected_area_array = numpy.array([
                [1, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]])
        expected_bounds = (0, 2, 0, 2)
        self.assertEqual(actual_result[:4], expected_bounds)
        self.assertTrue(
                numpy.array_equal(actual_result[4], expected_area_array))

        actual_result = img_lib.traverse_area_helper(array, (7, 1))
        expected_area_array = numpy.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0, 0]])
        expected_bounds = (6, 7, 0, 2)
        self.assertEqual(actual_result[:4], expected_bounds)
        self.assertTrue(
                numpy.array_equal(actual_result[4], expected_area_array))

        actual_result = img_lib.traverse_area_helper(array, (5, 7))
        expected_area_array = numpy.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1, 0]])
        expected_bounds = (5, 7, 5, 7)
        self.assertEqual(actual_result[:4], expected_bounds)
        self.assertTrue(
                numpy.array_equal(actual_result[4], expected_area_array))

        actual_result = img_lib.traverse_area_helper(array, (7, 4))
        expected_area_array = numpy.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 0]])
        expected_bounds = (6, 7, 4, 4)
        self.assertEqual(actual_result[:4], expected_bounds)
        self.assertTrue(
                numpy.array_equal(actual_result[4], expected_area_array))

    def test_get_area(self):
        array = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 1, 0]])

        area = img_lib.get_area(array, (0, 0))
        self.assertEqual(area['size'], 9)
        self.assertEqual(area['height'], 3)
        self.assertEqual(area['width'], 3)
        self.assertEqual(area['center'], (1, 1))

        area = img_lib.get_area(array, (6, 2))
        self.assertEqual(area['size'], 4)
        self.assertEqual(area['height'], 2)
        self.assertEqual(area['width'], 3)
        self.assertEqual(area['center'], (6, 1))

        area = img_lib.get_area(array, (5, 5))
        self.assertEqual(area['size'], 5)
        self.assertEqual(area['height'], 3)
        self.assertEqual(area['width'], 3)
        self.assertEqual(area['center'], (6, 6))

        area = img_lib.get_area(array, (7, 4))
        self.assertEqual(area['size'], 2)
        self.assertEqual(area['height'], 2)
        self.assertEqual(area['width'], 1)
        self.assertEqual(area['center'], (6, 4))

    def test_min_area_filter(self):
        array = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 1, 0]])
        image = SimpleITK.GetImageFromArray(array)
        min_area = 4
        
        image = img_lib.min_area_filter(image, min_area)
        actual = SimpleITK.GetArrayFromImage(image)
        expected = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 1, 0],
                [1, 1, 1, 0, 0, 0, 1, 0]])

        numpy.testing.assert_array_equal(expected, actual)

    def test_min_area_filter_array(self):
        array = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 1, 0]])
        min_area = 4
 
        img_lib.min_area_filter_array(array, min_area)
        # with numpy.printoptions(threshold=numpy.inf):
        #     print(array)

        expected = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 0, 0, 1, 0],
                [1, 1, 1, 0, 0, 0, 1, 0]])

        numpy.testing.assert_array_equal(expected, array)

    def test_set_area(self):
        array = numpy.array([
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 0, 0, 0, 1, 0],
                [1, 1, 1, 0, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 1, 1, 1, 1, 0, 1],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 0]])
    
        expectations = [
                {
                    'position': (0, 0),
                    'area': 0,
                },
                {
                    'position': (0, 1),
                    'area': 6,
                },
                {
                    'position': (1, 0),
                    'area': 0,
                },
                {
                    'position': (4, 7),
                    'area': 7,
                },
                {
                    'position': (0, 6),
                    'area': 7,
                },
                {
                    'position': (6, 1),
                    'area': 0,
                },
                {
                    'position': (7, 2),
                    'area': 11,
                },
        ]
        
        for expectation in expectations:
            actual = img_lib.set_area(array, expectation['position'])
            self.assertEqual(
                    expectation['area'],
                    actual,
                    "Expected '%s', got '%s' for area at %s" % (
                        expectation['area'],
                        actual,
                        expectation['position']))

    def test_set_area_with_visited(self):
        array = numpy.array([
                [0, 1, 0],
                [0, 1, 1],
                [1, 1, 1]])

        expectations = [
                {
                    'position': (0, 0),
                    'area': 0,
                },
                {
                    'position': (0, 1),
                    'area': 4,
                },
                {
                    'position': (1, 2),
                    'area': 4,
                },
                {
                    'position': (2, 0),
                    'area': 0,
                },
                {
                    'position': (2, 1),
                    'area': 4,
                },
                {
                    'position': (2, 2),
                    'area': 0,
                }
        ]
        
        for expectation in expectations:
            visited = numpy.array([
                    [0, 0, 0],
                    [0, 0, 0],
                    [1, 0, 1]])
 
            actual = img_lib.set_area(array, expectation['position'], visited)
            self.assertEqual(
                    expectation['area'],
                    actual,
                    "Expected '%s', got '%s' for area at %s" % (
                        expectation['area'],
                        actual,
                        expectation['position']))

            if not visited[expectation['position']]:
                self.assertNotEqual(
                        numpy.array([
                                [0, 0, 0],
                                [0, 0, 0],
                                [1, 0, 1]]),
                        visited,
                        "Expected visited array to change for area at %s" % (
                            expectation['position']))

    def test_max(self):
        array_1 = numpy.array([
                [1, 1, 0],
                [1, 0, 0],
                [0, 0, 0]])
        img_1 = SimpleITK.GetImageFromArray(array_1)
        array_2 = numpy.array([
                [0, 0, 0],
                [0, 0, 1],
                [0, 1, 1]])
        img_2 = SimpleITK.GetImageFromArray(array_2)
        array_3 = numpy.array([
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]])
        img_3 = SimpleITK.GetImageFromArray(array_3)

        actual = img_lib.max(img_1, img_2, img_3)
        actual_array = SimpleITK.GetArrayFromImage(actual)
        expected_array = numpy.array([
            [1, 1, 0],
            [1, 1, 1],
            [0, 1, 1]])

        numpy.testing.assert_array_equal(actual_array, expected_array)

    def test_get_all_areas_array(self):
        array = numpy.array([
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0, 1, 0]])
        areas = list(img_lib.get_all_areas_array(array, img_lib.Direction.UP))
        expected_areas = [
                {'size': 5, 'height': 3, 'width': 3, 'center': (6, 6)},
                {'size': 2, 'height': 2, 'width': 1, 'center': (6, 4)},
                {'size': 4, 'height': 2, 'width': 3, 'center': (6, 1)},
                {'size': 3, 'height': 1, 'width': 3, 'center': (4, 1)},
                {'size': 1, 'height': 1, 'width': 1, 'center': (3, 7)},
                {'size': 9, 'height': 3, 'width': 3, 'center': (1, 1)},
                {'size': 4, 'height': 2, 'width': 2, 'center': (0, 6)}]
        for expected_area in expected_areas:
            def area_in(exp_area, act_areas):
                for act_area in act_areas:
                    for key in exp_area:
                        if exp_area[key] != act_area[key]:
                            continue
                    return True
                return False

            self.assertTrue(area_in(expected_area, areas))

    def test_get_canal_row_px_from_disk_area(self):
        array = numpy.array([
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 1, 1, 1, 1, 1, 0]])
        area = list(img_lib.get_all_areas_array(array))[1]

        actual_slice = img_lib.get_canal_row_px_from_disk_area(array, area)
        self.assertEqual(actual_slice, 3)


if __name__ == '__main__':
    unittest.main()
