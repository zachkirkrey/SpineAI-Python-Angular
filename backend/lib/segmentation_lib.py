"""Library for representing segmentation information."""

from enum import IntEnum
import json
import logging
import math
import os
from pathlib import Path
import tempfile

from levelfinder.levelfinder import LevelFinder
import numpy
import scipy
import SimpleITK

from lib import img_lib
from lib import series_lib
from lib import util_lib

from lib import schema


MODEL_PATH = os.path.join(Path().absolute(), 'bin/levelfinder/state_dict.pt')

class SegmentationError(Exception):
    pass


class SegmentationMixin(object):
    """Member methods for schema.Segmentation."""

    def to_dir(self, file_path, file_type='png'):
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)

        if self.preprocessed_patient_series:
            preprocessed_path = os.path.join(file_path, 'preprocessed_patient_series')
            if not os.path.exists(preprocessed_path):
                os.makedirs(preprocessed_path, exist_ok=True)
            self.preprocessed_patient_series.to_dir(preprocessed_path, file_type='png')

        raw_path = os.path.join(file_path, 'raw_segmentation_series')
        if not os.path.exists(raw_path):
            os.makedirs(raw_path, exist_ok=True)
        img_lib.pretty_write_segmentation_img(
                self.raw_segmentation_series.image,
                raw_path)

        postprocessed_path = os.path.join(file_path, 'postprocessed_segmentation_series')
        if not os.path.exists(postprocessed_path):
            os.makedirs(postprocessed_path, exist_ok=True)
        img_lib.pretty_write_segmentation_img(
                self.postprocessed_segmentation_series.image,
                postprocessed_path)

class Segmentation(object):
    """Segmentation contains information about a completed segmentation."""

    @property
    def series(self):
        return self.segmentation.postprocessed_segmentation_series

    @staticmethod
    def postprocess(image, settings=None):
        """Performs segmentation post-processing to improve results."""
        raise NotImplementedError()


# TODO(billy): Refactor out repeated code between this class and ForamenSegmentation.
class CanalSegmentationMixin(Segmentation):
    """Series and segmentation information for a canal."""

    @staticmethod
    def postprocess(image, settings=None):
        if not settings:
            settings = {
                    'min_area_filter': 20,
            }

        new_image = img_lib.min_area_filter(image, settings['min_area_filter'])
        orig_image_array = SimpleITK.GetArrayFromImage(new_image)
        image_array = SimpleITK.GetArrayFromImage(new_image)

        # Remove all but the largest area if there are > 1 areas.
        for i, image_slice in enumerate(image_array):
            areas = list(img_lib.get_all_areas_array(image_slice))
            if len(areas) > 1:
                areas.sort(key=lambda area: area['size'], reverse=True)
                for area in areas[1:]:
                    img_lib.set_area(image_slice, area['sample_point'], new_value=0)
                    image_array[i] = image_slice

        # Peform a degree 3 polynomial curve-fit on area centers, and detect and fix outliers.
        def poly3(x, a, b, c, d):
            # return a * x**3 + b * x**2 + c * x + d
            return c * x + d

        no_area_slices = []
        num_area_slices = 0
        area_center_xdata = []
        area_center_ydata = []

        for i, image_slice in enumerate(image_array):
            areas = list(img_lib.get_all_areas_array(image_slice))
            if len(areas):
                num_area_slices += 1
                area_center_xdata.append(areas[0]['center'][0])
                area_center_ydata.append(areas[0]['center'][1])
            else:
                no_area_slices.append(i)

        # Perform least-squares curve fit.
        xopts, _ = scipy.optimize.curve_fit(
                poly3, list(range(num_area_slices)), area_center_xdata)
        yopts, _ = scipy.optimize.curve_fit(
                poly3, list(range(num_area_slices)), area_center_ydata)

        # Select the areas with the least distance to the curve.
        for i, image_slice in enumerate(orig_image_array):
            areas = list(img_lib.get_all_areas_array(image_slice))
            if len(areas) > 1:
                for area in areas:
                    poly3_slice_num = i + len([s for s in no_area_slices if s < i])
                    expected_x = poly3(poly3_slice_num, *xopts)
                    expected_y = poly3(poly3_slice_num, *yopts)

                    distance = math.sqrt(
                            (area['center'][0] - expected_x) ** 2 +
                            (area['center'][1] - expected_y) ** 2)

                    area['distance'] = distance

                areas.sort(key=lambda area: area['distance'])
                for area in areas[1:]:
                    img_lib.set_area(image_slice, area['sample_point'], new_value=0)
                    image_array[i] = image_slice

        new_image = SimpleITK.GetImageFromArray(image_array)
        new_image.CopyInformation(image)

        return new_image

    def get_num_slices(self):
        return self.series.image.GetDepth()

    def get_percentage_of_nearest_slices_for_indicies(self, canal_indicies, pixel_spacing):
        """Returns the area_of_canal / area_of_canal_of_nearest_slices.

        Returns:
            list(float) or None on error
        """
        # canal_indicies = [self.get_nearest_index_from_mm(l) for l in Zs]

        out = []

        # TODO(billy): Considering refactoring all the CanalSegmentation calls
        # to be cleaner and more efficient.
        canal_areas = self.get_canal_areas_for_indicies(canal_indicies, pixel_spacing)

        for i, canal_index in enumerate(canal_indicies):
            area = canal_areas[i]

            neighboring_indicies = []
            if canal_index > 0:
                neighboring_indicies.append(canal_index - 1)
            if canal_index < self.get_num_slices() - 1:
                neighboring_indicies.append(canal_index + 1)
            if not neighboring_indicies:
                return None
            neighboring_areas = self.get_canal_areas_for_indicies(neighboring_indicies, pixel_spacing)
            average_neighboring_area = sum(neighboring_areas) / len(neighboring_areas)

            if average_neighboring_area > 0:
                out.append(area / average_neighboring_area)
            else:
                # TODO(billy): Handle the error where the disk model is inaccurate.
                out.append(0)

        return out

    # TODO(billy) Write unit tests for this method.
    # def get_canal_areas_for_Z_mm(self, Zs, pixel_spacing):
    #     """Returns a list of canal segmentation areas for the given Zs in mm^2.

    #     Args:
    #         Zs: list(float) List of Z-axis measurements in mm's, relative to
    #             the DICOM absolute axis. Usually fetched from DiskSegmentation.
    #         pixel_spacing: tuple(float, float) Pixel spacing for canal
    #             segmentation.

    #     Returns:
    #         list(float) One area for each Z-axis value in Zs.
    #     """
    #     canal_indicies = [self.get_nearest_index_from_mm(l) for l in Zs]

    #     return self.get_canal_areas_for_indicies(canal_indicies, pixel_spacing)

    def get_disc_levels(self):
        levelfinder = LevelFinder(model_path=MODEL_PATH)
        image_array = SimpleITK.GetArrayFromImage(self.series.image)
        image_slices = []
        for s in image_array:
            image_slices.append(s)
        levels = levelfinder.find_slices(image_array).tolist()
        levels.sort()
        return levels

    def get_all_canal_areas(self):
        if self.segmentation.preprocessed_patient_series.metadata:
            pixel_spacing = self.segmentation.preprocessed_patient_series.metadata[0x00280030].value
        else:
            pixel_spacing = [1.0, 1.0, 1.0]
        num_slices = self.series.image.GetDepth()

        return self.get_canal_areas_for_indicies(range(num_slices), pixel_spacing)

    def get_canal_areas_for_indicies(self, indicies, pixel_spacing):
        canal_areas = []

        canal_image_array = SimpleITK.GetArrayFromImage(self.series.image)
        for i in indicies:
            areas = list(img_lib.get_all_areas_array(canal_image_array[i]))
            if len(areas) > 1:
                logging.warning(
                        'More than one area detected in canal segmentation. '
                        'Reporting largest...')
                areas.sort(key=lambda area: area['size'], reverse=True)

            if len(areas):
                canal_areas.append(areas[0]['size'] * pixel_spacing[0] * pixel_spacing[1])
            else:
                canal_areas.append(0)

        return canal_areas

    # def get_nearest_index_from_mm(self, Z):
    #     """Returns the index of the slice nearest to the given Z position."""
    #     # TODO(billy): To be proper here, we should use the image orientation
    #     # data from the DICOM image to align us to the RCS.
    #     origin_Z = self.series.image.GetOrigin()[2]
    #     if self.series.metadata:
    #         spacing_Z = self.series.metadata[0x00180088].value
    #     else:
    #         spacing_Z = 1.0

    #     num_slices = self.series.image.GetDepth()

    #     slice_locations_mm = []
    #     for i in range(num_slices):
    #         # TODO(billy): Check "addition" asumption based on orientation here.
    #         # TODO(billy): This may require abstracting orientation info and
    #         # making it globally available.
    #         slice_locations_mm.append(origin_Z + i * spacing_Z)

    #     # Return the index of value in slice_locations_mm closest to Z.
    #     if Z <= slice_locations_mm[0]:
    #         return 0
    #     for i, loc in enumerate(slice_locations_mm[:-1]):
    #         loc_next = slice_locations_mm[i + 1]
    #         if Z > loc and Z <= loc_next:
    #             left_diff = abs(Z - loc)
    #             right_diff = abs(Z - loc_next)
    #             if left_diff < right_diff:
    #                 return i
    #             else:
    #                 return i + 1
    #     return len(slice_locations_mm) - 1

    def get_expected_areas(self, age, height, sex):
        """Returns expected canal areas for the given demographic.

        Args:
            age: (float|int) Patient's age, in years.
            height: (int|float) Patient's height, in inches.
            sex: (schema.PatientSex) Enum representing patient's sex, Numerically 0
                for males and 1 for females. Defaults to 0.5 for unknown values.

        Returns:
            list(float) Expected canal values for L5/S1 -> L1/L2, respectively.
        """
        # TODO(billy): Move constants like this into a configuration file.
        weights = [
                { 'intercept': -258.99, 'age': -0.15, 'sex': -15.11, 'height': 7.38, 'height_sex': -0.12 },  # L5/S1
                { 'intercept': -273.87, 'age': -0.10, 'sex': 4.99, 'height': 7.75, 'height_sex': -0.58 },  # L4/L5
                { 'intercept': -249.79, 'age': 0.10, 'sex': -8.12, 'height': 7.47, 'height_sex': -0.38 },  # L3/L4
                { 'intercept': -283.04, 'age': 0.18, 'sex': -.37, 'height': 8.29, 'height_sex': -0.53 },  # L2/L3
                { 'intercept': -325.22, 'age': 0.22, 'sex': 15.43, 'height': 9.12, 'height_sex': -0.7 }]  # L1/L2

        out = []

        if sex == schema.PatientSex.MALE:
            sex = 0
        elif sex == schema.PatientSex.FEMALE:
            sex = 1
        else:
            sex = 0.5

        for weight in weights:
            area = weight['intercept'] + weight['age'] * age + weight['sex'] * sex + weight['height'] * height + weight['height_sex'] * height * sex
            out.append(area)

        return out


class DiskSegmentationMixin(Segmentation):
    """Series and segmentation information for spinal discs."""

    @staticmethod
    def postprocess(image, settings=None):
        if not settings:
            settings = {
                'min_area_filter': 40,
            }
        image_array = SimpleITK.GetArrayFromImage(image)

        new_image = SimpleITK.GetImageFromArray(image_array)

        if settings['min_area_filter']:
            new_image = img_lib.min_area_filter(
                    new_image,
                    settings['min_area_filter'])

        new_image.CopyInformation(image)
        return new_image

    def get_middle_disk_image(self):
        """Get the segmentation image of the middle slice."""
        image_array = SimpleITK.GetArrayFromImage(self.series.image)
        middle_slice = image_array[int(len(image_array) / 2)]

        return SimpleITK.GetImageFromArray(middle_slice)

    # def get_disk_locations_px(self):
    #     """Return the Z axis locations of each disk segment.

    #     TODO(billy): Document assumptions made here.
    #     """
    #     image_array = SimpleITK.GetArrayFromImage(self.series.image)

    #     middle_slice = image_array[int(len(image_array) / 2)]
    #     areas = list(img_lib.get_all_areas_array(middle_slice))

    #     canal_locations_px = []
    #     for area in areas:
    #         canal_locations_px.append(
    #                 img_lib.get_canal_row_px_from_disk_area(middle_slice, area))
    #     return canal_locations_px

    # def get_disk_locations_mm(self):
    #     """Return the Z axis locations of each disk segment."""
    #     # TODO(billy): To be proper here, we should use the image orientation
    #     # data from the DICOM image to align us to the RCS.
    #     canal_locations_px = self.get_disk_locations_px()

    #     origin_patient_Z = self.series.image.GetOrigin()[2]
    #     if self.series.metadata:
    #         row_pixel_spacing = self.series.metadata[0x00280030].value[0]
    #     else:
    #         row_pixel_spacing = 1.0

    #     # TODO(billy): Check math assumptions here based on orientation of image.
    #     # TODO(billy): Consider globally abstracting image orientation into a
    #     # helper class so we don't have to do any manual math.
    #     canal_locations_mm = []
    #     for px in canal_locations_px:
    #         canal_locations_mm.append(origin_patient_Z - row_pixel_spacing * px)
    #     return canal_locations_mm


class ForamenSegmentationMixin(Segmentation):
    """Series and segmentation information for an intervertebral foramen segmentation."""

    @staticmethod
    def postprocess(image, settings=None):
        """Performs segmentation post-processing to improve results."""
        if not settings:
            settings = {
                'min_area_filter': 40,
            }

        image_array = SimpleITK.GetArrayFromImage(image)

        new_image = SimpleITK.GetImageFromArray(image_array)

        if settings['min_area_filter']:
            new_image = img_lib.min_area_filter(
                    new_image,
                    settings['min_area_filter'])

        new_image.CopyInformation(image)
        return new_image

    def _data(self):
        data = {}

        if self.series:
            max_area_slices = self._calculate_max_area_slices()
            data.update({
                'max_area_slice': {
                    'left': max_area_slices[0],
                    'right': max_area_slices[1],
                }
            })

        seg_sizes = self.get_segmentation_sizes()
        data.update({
            'segmentation_sizes': seg_sizes
        })

        (left_areas, right_areas) = self.get_segmentation_union_areas()
        data.update({
            'segmentation_areas': {
                'left': left_areas,
                'right': right_areas,
            }
        })

        return data

    def to_json(self):
        return json.dumps(self._data())

    def get_standard_deviations(self):
        """Returns the std. dev. of the population model regression.

        This is the estimate of the standard deviation given by the standard
        error of the residuals of the population model explained and estimated
        in get_expected_areas().

        Returns:
            {'left': list(float), 'right': list(float)} Std. dev.s for foramina
                areas for L5/S1 -> L1/L2.
        """
        return {
                'left': [35.54, 35.36, 34.59, 31.64, 31.39],
                'right': [37.41, 35.48, 33.28, 30.72, 30.16],
        }

    def get_expected_areas(self, age, height, sex):
        """Gets the population median values for the L1-L5 foramina size.

        See paper: https://pubs.rsna.org/doi/full/10.1148/ryai.2019180037

        Args:
            age: (int) Integer value of patient's age.
            height: (int|float) Value of patient's height, in inches.
            sex: (PatientSex) Enum representing patient's sex, Numerically 0
                for males and 1 for females. Defaults to 0.5 for unknown values.

        Returns:
            {'left': list(float), 'right': list(float)} Left and right values
                of L5/S1 -> L1/L2 foramina, respetively.
        """
        weights = {
                'left': [
                    { 'intercept': -33.07055, 'age': -0.18727, 'sex': 58.26494, 'height': 2.70633, 'height_sex': -0.95578 },
                    { 'intercept': -6.49388, 'age': -0.27603, 'sex': 6.92597, 'height': 2.48785, 'height_sex': -0.15566 },
                    { 'intercept': -26.36734, 'age': -0.46201, 'sex': 33.26441, 'height': 3.08723, 'height_sex': -0.61079 },
                    { 'intercept': -9.4282, 'age': -0.3261, 'sex': -31.0449, 'height': 2.6182, 'height_sex': -0.3233 },
                    { 'intercept': -13.374443, 'age': -0.365960, 'sex': -9.996693, 'height': 2.488577, 'height_sex': -0.002277 }],
                'right': [
                    { 'intercept': -3.43599, 'age': -0.24579, 'sex': 73.81479, 'height': 2.22283, 'height_sex': -1.07568 },
                    { 'intercept': 29.15354, 'age': -0.33057, 'sex': 4.44157, 'height': 2.00105, 'height_sex': -0.10410 },
                    { 'intercept': -37.57504, 'age': -0.40725, 'sex': 80.19229, 'height': 3.15502, 'height_sex': -1.30814 },
                    { 'intercept': -39.11850, 'age': -0.36410, 'sex': 33.17530, 'height': 3.01178, 'height_sex': -0.58945 },
                    { 'intercept': -29.27072, 'age': -0.36796, 'sex': 56.58323, 'height': 2.70222, 'height_sex': -0.96443 }],
        }

        out = {
                'left': [],
                'right': [],
        }

        # TODO(billy): Create module so logs are written to a per-study location for debugging.
        if sex != PatientSex.MALE and sex != PatientSex.FEMALE:
            logging.warn('Unknown patient sex. Using average...')
            sex = 0.5
        else:
            sex = sex.value

        for key in out:
            for weight in weights[key]:
                area = weight['intercept'] + weight['age'] * age + weight['sex'] * sex + weight['height'] * height + weight['height_sex'] * height * sex
                out[key].append(area)

        return out

    def get_z_values(self, age, height, sex):
        """Returns the (actual - expected)/std_dev for each segmentation.

        Returns:
            {'left': list(float), 'right': list(float)}
        """
        segmentation_sizes = self.get_segmentation_sizes()
        expected_areas = self.get_expected_areas(age, height, sex)
        standard_deviations = self.get_standard_deviations()

        out = {}
        for side in ('left', 'right'):
            out[side] = []
            # We process the number of foramina segmented, or 5, whichever is
            # smaller.
            for i in range(min(len(segmentation_sizes[side]), 5)):
                z_value = (segmentation_sizes[side][i] - expected_areas[side][i]) / standard_deviations[side][i]
                out[side].append(z_value)

        return out


    def get_segmentation_union_areas(self):
        """Returns metadata about the segmentation areas."""
        (left_seg_img, right_seg_img) = self.get_segmentation_union_images()

        left_seg_array = SimpleITK.GetArrayFromImage(left_seg_img)
        right_seg_array = SimpleITK.GetArrayFromImage(right_seg_img)

        left_areas = list(img_lib.get_all_areas_array(left_seg_array))
        right_areas = list(img_lib.get_all_areas_array(right_seg_array))

        return (left_areas, right_areas)

    def get_segmentation_union_images(self):
        """Returns the maximum image projection (union) of segmentations.

        Returns:
            (image, image) Left and right segmentation unions, respectively.
        """
        # TODO(billy): This and _calculate_max_area_slices() basically do the
        # same thing, can probably optimize/cache some results.

        # TODO(billy): Consider normalizing all pixels to [0, 1] for later 
        # * 255 conversion.
        image_array = SimpleITK.GetArrayFromImage(self.series.image)
        if len(image_array.shape) != 3:
            raise TypeError(
                    'Expected 3-dimensional image shape. got: %s' %
                    str(image_array.shape))

        (num_slices, X, Y) = image_array.shape
        if num_slices < 2:
            raise TypeError(
                    'Expected at least 2 slices. got: %d' % num_slices)

        left_image_array = numpy.zeros((X, Y))
        for i in range(num_slices // 2):
            left_image_array = img_lib.max_array(image_array[i], left_image_array)

        right_image_array = numpy.zeros((X, Y))
        for i in range((num_slices // 2 + (num_slices % 2)), num_slices):
            right_image_array = img_lib.max_array(image_array[i], right_image_array)

        return (SimpleITK.GetImageFromArray(left_image_array * 255),
                SimpleITK.GetImageFromArray(right_image_array * 255))

    def _calculate_max_area_slices(self):
        """Returns the slices that have the biggest foraminal area.

        Returns a 2-tuple (left, right), where left and right are the indicies
        of the slices that contain the largest segmentation area on the left
        and right ,respectively.
        """
        # TODO(billy): Allow caching of this result.
        image_array = SimpleITK.GetArrayFromImage(self.series.image)
        if len(image_array.shape) != 3:
            raise TypeError(
                    'Expected 3-dimensional image shape. got: %s' %
                    str(image_array.shape))

        (num_slices, _, _) = image_array.shape
        if num_slices < 2:
            raise TypeError(
                    'Expected at least 2 slices. got: %d' % num_slices)

        left_slice = None
        left_max_area = -1
        for i in range(num_slices // 2):
            area = sum([
                area['size'] for area in img_lib.get_all_areas_array(image_array[i])])
            if area > left_max_area:
                left_max_area = area
                left_slice = i

        right_slice = None
        right_max_area = -1
        for i in range((num_slices // 2 + (num_slices % 2)), num_slices):
            area = sum([
                area['size'] for area in img_lib.get_all_areas_array(image_array[i])])
            if area > right_max_area:
                right_max_area = area
                right_slice = i

        return (left_slice, right_slice)

    def get_segmentation_sizes(self):
        seg_sizes = self._calculate_segmentation_sizes_pixels()
        for side in seg_sizes:
            for i in range(len(seg_sizes[side])):
                area_pixels = seg_sizes[side][i]
                area_mm = area_pixels * self.series.get_pixel_area()
                seg_sizes[side][i] = area_mm

        return seg_sizes

    def _calculate_segmentation_sizes_pixels(self):
        """Calculate the real-value segmentation sizes of the given images."""

        # We assume here that slices are increasing towards the right of the
        # patient, as this is true for our base set.
        # TODO(billy): Store the DICOM orientation data and infer orientation 
        # from that instead.

        # We also assume one series.
        # TODO(billy): Refactor code base to only accept assume one series.
        if self.series is None:
            raise SegmentationError(
                    '_calculate_segmentation_sizes(): No series to size.')

        image_array = SimpleITK.GetArrayFromImage(self.series.image)
        if len(image_array.shape) != 3:
            raise TypeError(
                    'Expected 3-dimensional image shape. got: %s' %
                    str(image_array.shape))

        (num_slices, _, _) = image_array.shape
        if num_slices < 2:
            raise TypeError(
                    'Expected at least 2 image slices. got: %d' % num_slices)
        # If len(image_array) is odd, discord the middle slice.
        left_arrays = image_array[:(num_slices // 2)]
        right_arrays = image_array[(num_slices // 2 + (num_slices % 2)):]

        left_segmentation = img_lib.max_array(*left_arrays)
        right_segmentation = img_lib.max_array(*right_arrays)

        segmentation_sizes = {
                'left': list([
                    area['size'] for area in img_lib.get_all_areas_array(left_segmentation)]),
                'right': list([
                    area['size'] for area in img_lib.get_all_areas_array(right_segmentation)]),
        }

        return segmentation_sizes
