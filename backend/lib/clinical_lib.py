"""Library for clinical decision making."""

from enum import IntEnum, auto

import numpy
import SimpleITK

from lib import study_lib


class MeasurementMixin(object):
    """Abstract base class for measurements."""

    def name(self):
        raise NotImplementedError()

    def get_measurements(self):
        raise NotImplementedError()


class CanalNarrowingMeasurement(MeasurementMixin):

    def __init__(self, canal_segmentation):
        self._canal_segmentation = canal_segmentation

        # Constants origninally taken from Bilwaj's spreadsheet:
        # https://drive.google.com/file/d/1Rfgs7rTHm6wgXfPMEb20Jm2-TjgqODvz/view?usp=sharing,
        # Then fine tuned by Sam Elhag:
        # https://drive.google.com/file/d/1fjzGmMBbv-7CgtueolF6OQHL_Ib--7Q8/view?usp=sharing
        self.narrowing_threshold = 0.2
        self.surgery_narrow_slices_threshold = 6

    def name(self):
        return "canal_narrowing"

    def get_measurements(self):
        num_slices = self._canal_segmentation.get_num_slices()

        narrowing = self._get_narrowing()
        num_narrow_slices = 0;
        for n in narrowing:
            if n > self.narrowing_threshold:
                num_narrow_slices += 1

        return {
            'num_slices': num_slices,
            'narrowing': narrowing,
            'num_narrow_slices': num_narrow_slices,
            'narrowing_threshold': self.narrowing_threshold,
            'narrow_slices_threshold': self.surgery_narrow_slices_threshold,
            'surgery_recommended': num_narrow_slices > self.surgery_narrow_slices_threshold,
        }

    def _get_narrowing(self):
        canal_areas = self._canal_segmentation.get_all_canal_areas()

        narrowing = []
        for i, area in enumerate(canal_areas):
            neighboring_areas = []
            if i > 0:
                neighboring_areas.append(canal_areas[i - 1])
            if i > 1:
                neighboring_areas.append(canal_areas[i - 2])
            if i < len(canal_areas) - 2:
                neighboring_areas.append(canal_areas[i + 2])
            if i < len(canal_areas) - 1:
                neighboring_areas.append(canal_areas[i + 1])

            neighboring_avg = sum(neighboring_areas) / len(neighboring_areas)
            slice_narrowing = 0
            if (neighboring_avg > 0):
                slice_narrowing = (neighboring_avg - area) / neighboring_avg
                if (slice_narrowing < 0):
                    slice_narrowing = 0

            narrowing.append(slice_narrowing)

        return narrowing


class CutlineBoundaryTypes(IntEnum):
    TOP_AND_BOTTOM = auto()
    LEFT_AND_RIGHT = auto()


class CutlineMeasurement(MeasurementMixin):

    def __init__(self, sagittal_series, axial_series):
        self._sagittal_series = sagittal_series
        self._axial_series = axial_series

    def name(self):
        return "cutlines"

    def _get_boundary_lines(self, series, boundary_type):
        """Returns lines defining the edges of of a series.

        Returns:
            list((unit_vector, top_point, bottom_point)) Where
                unit_vector is a unit vector in the direction of each line.
                top_point is a point in the line at the top of the image.
                bottom_point is a point in the line at the bottom of the image.
                Values are returned in 3D patient coordinates in mm. (x,y,z)
        """
        lines = []

        num_slices = series.image.GetDepth()

        for num_slice in range(num_slices):
            if len(series.metadatas) == num_slices:
                img_orientation = series.metadatas[num_slice][0x00200037].value
            else:
                img_orientation = series.metadata[0x00200037].value

            if boundary_type == CutlineBoundaryTypes.TOP_AND_BOTTOM:
                unit_vector = numpy.asarray(img_orientation[:3])
            elif boundary_type == CutlineBoundaryTypes.LEFT_AND_RIGHT:
                unit_vector = numpy.asarray(img_orientation[3:])
            else:
                raise ValueError('Unknown BoundaryType: {}', boundary_type)

            unit_vector = unit_vector / numpy.linalg.norm(unit_vector)
            top_left_point = series.get_patient_coordinates(
                    (num_slice, 0, 0))
            bottom_right_point = series.get_patient_coordinates(
                    (num_slice, series.image.GetHeight(),
                     series.image.GetWidth()))

            lines.append((unit_vector, top_left_point, bottom_right_point))

        return lines

    def _get_cutlines(self, series, lines):
        """Returns the cutlines defined by the intersection of series and lines.

        Returns:
            list(list(cutlines)) A list of lists, 1 per slice in series, where
                each cutline is a (point, point) tuple, and each point is a
                (row, column) tuple.
        """
        cutlines = []
        num_slices = series.image.GetDepth()

        for num_slice in range(num_slices):
            slice_cutlines = []

            if len(series.metadatas) == num_slices:
                if len(series.metadatas) == num_slices:
                    img_orientation = series.metadatas[num_slice][0x00200037].value
                else:
                    img_orientation = series.metadata[0x00200037].value

            row_unit_vector = numpy.asarray(img_orientation[:3])
            col_unit_vector = numpy.asarray(img_orientation[3:])
            depth_unit_vector = numpy.cross(row_unit_vector, col_unit_vector)

            plane_point = series.get_patient_coordinates((num_slice, 0, 0))

            for (line_unit_vector, top_point, bottom_point) in lines:
                top_intersection = self.line_plane_intersection(
                        depth_unit_vector, plane_point,
                        line_unit_vector, top_point)
                top_intersection_px = series.get_pixel_coordinates(top_intersection)

                bottom_intersection = self.line_plane_intersection(
                        depth_unit_vector, plane_point,
                        line_unit_vector, bottom_point)
                bottom_intersection_px = series.get_pixel_coordinates(bottom_intersection)

                slice_cutlines.append((
                    top_intersection_px[1:].tolist(),
                    bottom_intersection_px[1:].tolist()))

            cutlines.append(slice_cutlines)

        return cutlines

    def get_measurements(self):
        """Returns cutline pixel coordinates for each sagittal slice."""
        if (not self._sagittal_series.metadatas or
            not self._axial_series.metadatas):
            return None

        ax_lines = self._get_boundary_lines(
                self._axial_series, CutlineBoundaryTypes.TOP_AND_BOTTOM)
        sag_lines = self._get_boundary_lines(
                self._sagittal_series, CutlineBoundaryTypes.LEFT_AND_RIGHT)

        ax_cutlines = self._get_cutlines(self._axial_series, sag_lines)
        sag_cutlines  = self._get_cutlines(self._sagittal_series, ax_lines)

        cutlines = {
                'axial': ax_cutlines,
                'sagittal': sag_cutlines,
        }

        return cutlines

    def line_plane_intersection(
            self,
            plane_normal, plane_point, ray_direction, ray_point,
            epsilon=1e-6):
        # Code from
        # https://www.rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
        # under the GNU Free Documentation License 1.2.
        ndotu = plane_normal.dot(ray_direction)
        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")
        w = ray_point - plane_point
        si = -plane_normal.dot(w) / ndotu
        Psi = w + si * ray_direction + plane_point
        return Psi

class GeisingerMeasurement(MeasurementMixin):

    def __init__(self, canal_segmentation):
        self._canal_segmentation = canal_segmentation

    def name(self):
        return "geisinger"

    def get_measurements(self):
        return {
                'canal_heights': self._get_canal_heights(),
                'canal_widths': self._get_canal_widths(),
        }

    def _get_canal_heights(self):
        canal_image_array = SimpleITK.GetArrayFromImage(self._canal_segmentation.series.image)

        canal_heights = []

        for slice_array in canal_image_array:
            nonzero = slice_array.nonzero()

            if len(nonzero[1]):
                # Get the median column.
                # (ie. the col for which half the pixels are on either side)
                median_col = int(numpy.median(nonzero[1]))
                median_rows = numpy.where(slice_array[:, median_col])

                origin = (int(numpy.min(median_rows)), int(median_col))
                px_height = int(numpy.max(median_rows) - numpy.min(median_rows) + 1)


                if self._canal_segmentation.series.metadata:
                    pixel_spacing = self._canal_segmentation.series.metadata[0x00280030].value
                else:
                    pixel_spacing = [1.0, 1.0, 1.0]
                height_spacing = pixel_spacing[0]
                display_height = round(px_height * height_spacing, 2)

                unit = 'mm'
                if height_spacing == 1:
                    unit = 'px'
            else:
                origin = (0, 0)
                px_height = 0
                display_height = 0
                unit = ''

            canal_heights.append({
                'origin': origin,
                'px_height': px_height,
                'display_height': display_height,
                'unit': unit,
            })

        return canal_heights

    def _get_canal_widths(self):
        canal_image_array = SimpleITK.GetArrayFromImage(self._canal_segmentation.series.image)

        canal_widths = []

        for slice_array in canal_image_array:
            nonzero = slice_array.nonzero()

            if len(nonzero[0]):
                max_width_row = 0
                max_width = 0
                origin_col = 0

                for row in set(nonzero[0]):
                    cols = numpy.where(slice_array[row , :])
                    width = int(numpy.max(cols) - numpy.min(cols)) + 1

                    if width > max_width:
                        max_width_row = row
                        max_width = width
                        origin_col = numpy.min(cols)

                if self._canal_segmentation.series.metadata:
                    pixel_spacing = self._canal_segmentation.series.metadata[0x00280030].value
                else:
                    pixel_spacing = [1.0, 1.0, 1.0]
                width_spacing = pixel_spacing[1]
                display_width = round(max_width * width_spacing, 2)

                unit = 'mm'
                if width_spacing == 1:
                    unit = 'px'
            else:
                max_width_row = 0
                max_width = 0
                origin_col = 0
                display_width = 0
                unit = ''

            canal_widths.append({
                'origin': (int(max_width_row), int(origin_col)),
                'px_width': max_width,
                'display_width': display_width,
                'unit': unit,
            })

        return canal_widths
