"""Unit tests for segmentation_lib.py"""

import json
import os
import tempfile

import SimpleITK

from testutil import unittest

from lib import img_lib
from lib import segmentation_lib
from lib import series_lib
from lib import study_lib


TEST_CANAL_SEGMENTATION = os.path.join(unittest.PROJECT_PATH, 'testdata/canal_segmentation.zip')
TEST_DISK_SEGMENTATION = os.path.join(unittest.PROJECT_PATH, 'testdata/disk_segmentation.zip')
TEST_FORAMEN_SEGMENTATION = os.path.join(unittest.PROJECT_PATH, 'testdata/foramen_segmentation.zip')


class SegmentationTest(unittest.TestCase):
    pass

    # def test_to_and_from_file(self):
    #     original_seg = segmentation_lib.CanalSegmentation.from_file(TEST_CANAL_SEGMENTATION)
    #     self.assertIsNotNone(original_seg.series)

    #     with tempfile.TemporaryDirectory() as tmp_dir:
    #         file_path = os.path.join(tmp_dir, 'seg.zip')
    #         original_seg.to_file(file_path)
    #         new_seg = segmentation_lib.Segmentation.from_file(file_path)

    #         self.assertIsNotNone(new_seg.series)

    # def test_to_dir(self):
    #     seg = segmentation_lib.CanalSegmentation.from_file(TEST_CANAL_SEGMENTATION)

    #     with tempfile.TemporaryDirectory() as tmp_dir:
    #         seg = seg.to_dir(tmp_dir)


class CanalSegmentationTest(unittest.TestCase):
    pass

    # def test_postprocess_leaves_only_one_area(self):
    #     seg = segmentation_lib.CanalSegmentation.from_file(TEST_CANAL_SEGMENTATION)
    #     image_array = SimpleITK.GetArrayFromImage(seg.series.image)
    #     self.assertEqual(
    #             len(image_array.shape), 3,
    #             'canal segmentation series not 3-dimensional. got: %d' % len(
    #                 image_array.shape))

    #     all_areas = [list(img_lib.get_all_areas_array(img)) for img in image_array]
    #     num_areas = sum([len(areas) for areas in all_areas])
    #     self.assertGreater(
    #             num_areas, 0,
    #             'Expected at least one canal segmentation area. got %d' % (
    #                 num_areas))

    #     # TODO(billy): If there isn't a slice with 2 areas, artifically create them.
    #     # self.assertIn(
    #     #         2, [len(areas) for areas in all_areas],
    #     #         'Expected a slice with 2 areas in test canal segmentation.')

    #     seg.postprocess()

    #     image_array = SimpleITK.GetArrayFromImage(seg.series.image)
    #     all_areas = [list(img_lib.get_all_areas_array(img)) for img in image_array]
    #     for i, areas in enumerate(all_areas):
    #         self.assertLessEqual(
    #                 len(areas), 1,
    #                 'Expected 1 or less areas in each canal slice, got %s in '
    #                 'slice %d' % (
    #                     areas, i))

    # TODO(billy): Fix test cases for these tests.
    # def test_get_canal_areas_for_Z_mm(self):
    #     seg = segmentation_lib.CanalSegmentation()
    #     seg.series = series_lib.PatientSeriesFromDICOMFiles(TEST_CANAL_SEGMENTATION)[0]
    #     seg.series.image.SetOrigin((-116.62049865722656, -80.77218627929688, -80.82357025146484))
    #     spacing = (0.78125, 0.78125, 5.625)
    #     seg.series.image.SetSpacing(spacing)

    #     Zs = [-44.74, -14.2738, 19.24, 54.79, 88.3, 120.8]
    #    
    #     expected_areas = [
    #             245.9716796875,
    #             205.078125,
    #             173.33984375,
    #             186.767578125,
    #             193.4814453125,
    #             214.84375]
    #     self.assertListEqual(
    #             seg.get_canal_areas_for_Z_mm(Zs, spacing),
    #             expected_areas)

    # def test_get_nearest_index_from_mm(self):
    #     seg = segmentation_lib.CanalSegmentation()
    #     seg.series = series_lib.PatientSeriesFromDICOMFiles(TEST_CANAL_SEGMENTATION)[0]
    #     
    #     seg.series.image.SetOrigin((-116.62049865722656, -80.77218627929688, -80.82357025146484))
    #     seg.series.image.SetSpacing((0.78125, 0.78125, 5.625))
    #     self.assertEqual(seg.series.image.GetDepth(), 40)
    #     
    #     self.assertEqual(seg.get_nearest_index_from_mm(-44.74), 6)
    #     self.assertEqual(seg.get_nearest_index_from_mm(-14.2738), 12)
    #     self.assertEqual(seg.get_nearest_index_from_mm(19.24), 18)
    #     self.assertEqual(seg.get_nearest_index_from_mm(54.79), 24)
    #     self.assertEqual(seg.get_nearest_index_from_mm(88.3), 30)
    #     self.assertEqual(seg.get_nearest_index_from_mm(120.8), 36)

    # def test_get_expected_areas(self):
    #     seg = segmentation_lib.CanalSegmentation()
    #     actual_medians = seg.get_expected_areas(50, 66, PatientSex.MALE)
    #     expected_medians = [
    #             220.58999999999997,
    #             232.63,
    #             248.23,
    #             273.09999999999997,
    #             287.69999999999993]
    #     self.assertEqual(actual_medians, expected_medians)
 


class DiskSegmentationTest(unittest.TestCase):
    pass
    # def __init__(self, *args, **kwargs):
    #     unittest.TestCase.__init__(self, *args, **kwargs)
    #     self.seg = segmentation_lib.DiskSegmentation.from_file(TEST_DISK_SEGMENTATION)

    #     self.seg.series.image.SetOrigin((43.407073974609375, -64.14043426513672, 123.84881591796875))

    #     self.seg.postprocess_settings['min_area_filter'] = 120
    #     self.seg.postprocess()

    # def test_postprocess_preserves_origin_and_spacing(self):
    #     seg = segmentation_lib.DiskSegmentation.from_file(TEST_DISK_SEGMENTATION)

    #     origin = (43.407073974609375, -64.14043426513672, 123.84881591796875)
    #     spacing = (0.8125, 0.8125, 4.799998760223389)
    #     self.assertNotEqual(seg.series.image.GetOrigin(), origin)
    #     self.assertNotEqual(seg.series.image.GetSpacing(), spacing)

    #     seg.series.image.SetOrigin(origin)
    #     seg.series.image.SetSpacing(spacing)

    #     seg.postprocess_settings['min_area_filter'] = 120
    #     seg.postprocess()

    #     self.assertEqual(seg.series.image.GetOrigin(), origin)
    #     self.assertEqual(seg.series.image.GetSpacing(), spacing)

    # def test_postprocess_min_area_filter(self):
    #     seg = segmentation_lib.ForamenSegmentation.from_file(TEST_FORAMEN_SEGMENTATION)
    #     
    #     seg.postprocess_settings['min_area_filter'] = 120

    #     image_array = SimpleITK.GetArrayFromImage(seg.series.image)
    #     all_areas = [list(img_lib.get_all_areas_array(img)) for img in image_array]
    #     all_areas = [item for sublist in all_areas for item in sublist]

    #     # Confirm at least one area is < min_area_filter.
    #     self.assertTrue(any(area['size'] < seg.postprocess_settings['min_area_filter'] for area in all_areas))

    #     seg.postprocess()

    #     image_array = SimpleITK.GetArrayFromImage(seg.series.image)
    #     all_areas = [list(img_lib.get_all_areas_array(img)) for img in image_array]
    #     all_areas = [item for sublist in all_areas for item in sublist]
    #     self.assertFalse(any(area['size'] < seg.postprocess_settings['min_area_filter'] for area in all_areas))

    # def test_get_disk_locations_px(self):
    #     disk_locations_px = self.seg.get_disk_locations_px()
    #     self.assertEqual(disk_locations_px, [222, 191, 155, 119, 83, 50, 20])

    # def test_get_disk_locations_mm(self):
    #     actual_disk_locations_mm = self.seg.get_disk_locations_mm()
    #     expected_disk_locations_mm = [
    #             -101.61993408203125,
    #             -70.13555908203125,
    #             -33.57305908203125,
    #             2.98944091796875,
    #             39.55194091796875,
    #             73.06756591796875,
    #             103.53631591796875]
    #     for actual, expected in  zip(actual_disk_locations_mm, expected_disk_locations_mm):
    #         self.assertAlmostEqual(actual, expected, delta=.01)


class ForamenSegmentationTest(unittest.TestCase):
    pass

    # def __init__(self, *args, **kwargs):
    #     unittest.TestCase.__init__(self, *args, **kwargs)
    #     self.seg = segmentation_lib.ForamenSegmentation.from_file(TEST_FORAMEN_SEGMENTATION)

    #     self.assertTrue(self.seg.series)

    # def test_segmentation_size(self):
    #     self.assertIsNotNone(self.seg.get_segmentation_sizes())

    # def test_max_area_slices(self):
    #     actual = self.seg._calculate_max_area_slices()
    #     expected = (3, 8)
    #     self.assertEqual(actual, expected)

    # def test_to_json(self):
    #     json_str = self.seg.to_json()
    #     obj = json.loads(json_str)

    # def test_get_segmentation_union_areas(self):
    #     (left_areas, right_areas) = self.seg.get_segmentation_union_areas()
    #     self.assertEqual(7, len(left_areas))
    #     self.assertEqual(8, len(right_areas))

    # def test_get_z_values(self):
    #     actual_z_values = self.seg.get_z_values(50, 66, PatientSex.MALE)
    #     expected_z_values = {
    #             'left': [
    #                 2.24581513787282,
    #                 1.4450588235294122,
    #                 1.7551506215669264,
    #                 0.3455120101137805,
    #                 0.5551564510990756],
    #             'right': [
    #                 -1.9241189521518314,
    #                 1.0514560315670791,
    #                 -0.8201256009615375,
    #                 1.0594407552083334,
    #                 1.9669164456233426]
    #             }
    #     self.assertDictEqual(expected_z_values, actual_z_values)

    # def test_get_expected_areas(self):
    #     seg = segmentation_lib.ForamenSegmentation()
    #     actual_medians = seg.get_expected_areas(50, 66, PatientSex.MALE)
    #     expected_medians = {
    #             'left': [
    #                 136.18372999999997,
    #                 143.90272,
    #                 154.28934,
    #                 147.06799999999998,
    #                 132.57363900000001],
    #             'right': [
    #                 130.98129,
    #                 144.69434000000004,
    #                 150.29377999999997,
    #                 141.45398,
    #                 130.6778]
    #     }
    #     self.assertDictEqual(actual_medians, expected_medians)


if __name__ == '__main__':
    unittest.main()
