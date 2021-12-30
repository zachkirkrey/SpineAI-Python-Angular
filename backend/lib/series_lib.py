"""Library for representing DICOM images as series."""

from collections import defaultdict
import glob
import json
from imread import imread
import logging
import numpy
import os
import pickle
import re
from shutil import copyfile
import skimage
import tempfile

import pydicom
import SimpleITK

from lib import dicom_lib
from lib import util_lib


class SeriesError(Exception):
    pass


def ImageSeriesFromDICOMFiles(study):
    """Returns ImageSeries objects for series in DICOM files.

    This function uses SimpleITK.ImageSeriesReader() to detect DICOM series in
    the given files. Note that multiple DICOM files can be a part of one
    series.

    See:
    https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction
    for an introduction on DICOM studies and series.

    Intended to ingest user-provided MRI images.

    Args:
        study: (schema.Study) Study with file_dir_path set.

    Returns:
        list(ImageSeries) One ImageSeries per DICOM series from
            study.file_dir_path.

    Raises:
        FileNotFoundError on no files matching in dir_path.
        SeriesError on no DICOM series detected in given files.
    """
    from lib import schema
    file_pattern = os.path.join(study.file_dir_path, '**', '*')
    paths = glob.glob(file_pattern, recursive=True)
    if len(paths) > 3000:
        logging.error(
                'Max. 3000 files per study. Found: {} paths in {}.'.format(
                    len(paths), study.file_dir_path))
        return []

    file_paths = [path for path in paths if os.path.isfile(path)]
    if not file_paths:
        raise FileNotFoundError('No files match pattern %s' % file_pattern)
    logging.info(
            'Reading %d files from %s' % (len(file_paths), file_pattern))

    # TODO(billy): Support ZIP archives.
    # TODO(billy): Re-support NIFTI files.

    all_series = []
    # SimpleITK prefers files in the same directory for series detection
    # between multiple files, so we move input files to a tmpdir.
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_num = 1
        for file_path in file_paths:
            file_name = str(file_num) + '.dcm'
            copyfile(file_path, os.path.join(tmpdirname, file_name))
            file_num += 1

        reader = SimpleITK.ImageSeriesReader()
        reader.SetOutputPixelType(SimpleITK.sitkFloat32)
        series_ids = reader.GetGDCMSeriesIDs(tmpdirname)
        if not series_ids:
            logging.warning('No DICOM series found in %s.' % file_pattern)

        def read_dicom_series(reader, file_paths):
            """Read the given DICOM files into an ImageSeries."""
            reader.SetFileNames(file_paths)
            try:
                image = reader.Execute()
            except RuntimeError as e:
                if len(file_paths) == 1:
                    logging.warning(
                            'RuntimeError ({}) while reading series. '
                            'Attempting ReadImage instead...'.format(str(e)))
                    image = SimpleITK.ReadImage(file_paths[0])
                else:
                    raise RuntimeError

            metadatas = []
            for path in file_paths:
                metadatas.append(pydicom.dcmread(path))

            return schema.ImageSeries(
                    type=schema.ImageSeriesType.PATIENT.name,
                    study=study,
                    metadata_pickled=pickle.dumps(metadatas),
                    image_pickled=pickle.dumps(image))

        for series_id in series_ids:
            # Handle series that are missing (0020,000E) Series Instance
            # UID.
            if series_id == '':
                logging.warning(
                        'Some or all DICOM files are missing (0020,000E) Series '
                        'Instance UID. Attempting to use (0020, 0011) Series '
                        'Number and (0020, 0013) Image Number.')
                dicom_file_paths = reader.GetGDCMSeriesFileNames(
                        tmpdirname, series_id)

                class DicomPath(object):
                    def __init__(self, path, image_number):
                        self.path = path
                        self.image_number = image_number

                paths_by_series = defaultdict(list)
                for path in dicom_file_paths:
                    metadata = pydicom.dcmread(path)
                    # (0020,0011) Series Number
                    if 0x00200011 in metadata:
                        series_number = str(metadata[0x00200011].value)
                    else:
                        raise RuntimeError(
                            'Could not determine series information from '
                            'DICOM file.')

                    # (0020,0013) Image Number
                    if 0x00200013 in metadata:
                        image_number = str(metadata[0x00200013].value)
                    else:
                        raise RuntimeError(
                            'Could not determine image information from '
                            'DICOM file.')

                    paths_by_series[series_number].append(
                            DicomPath(path, image_number))

                for series_number in paths_by_series:
                    sorted_paths = [p.path for p in sorted(
                        paths_by_series[series_number], key=lambda dp: dp.image_number)]
                    series = read_dicom_series(reader, sorted_paths)
                    all_series.append(series)

                continue


            dicom_file_paths = reader.GetGDCMSeriesFileNames(
                    tmpdirname, series_id)

            try:
                series = read_dicom_series(reader, dicom_file_paths)
            except RuntimeError as e:
                logging.error(
                        'RuntimeError (%s) while reading series.', str(e))
                continue
            all_series.append(series)

    return all_series

def ImageSeriesFromJPEGFiles(study):
    from lib import schema
    file_pattern = os.path.join(study.file_dir_path, '**', '*')
    paths = glob.glob(file_pattern, recursive=True)
    if len(paths) > 3000:
        logging.error(
                'Max. 3000 files per study. Found: {} paths in {}.'.format(
                    len(paths), study.file_dir_path))
        return []

    file_paths = [path for path in paths if os.path.isfile(path)]
    if not file_paths:
        raise FileNotFoundError('No files match pattern %s' % file_pattern)

    logging.info(
            'Processing %d files from %s' % (len(file_paths), file_pattern))

    axial_image_paths = []
    sagittal_image_paths = []
    ax_re = re.compile('ax.*\.jpg')
    sag_re = re.compile('sag.*\.jpg')
    for path in file_paths:
        filename = os.path.basename(path)
        if ax_re.match(filename.lower()):
            axial_image_paths.append(path)
        elif sag_re.match(filename.lower()):
            sagittal_image_paths.append(path)

    if not (axial_image_paths and sagittal_image_paths):
        logging.error(
            'JPEG files must contain at least one axial image beginning with '
            '"ax" and one sagittal image beginning with "sag".')
        return []

    def get_image_from_jpeg_paths(jpeg_paths):
        """
        Returns:
            (SimpleITK.Image)
        """
        jpeg_paths = sorted(jpeg_paths)
        # Determine JPEG image size.
        jpg_array = skimage.color.rgb2gray(imread(jpeg_paths[0]))
        skimage_array = numpy.ndarray(
                shape=(len(jpeg_paths), jpg_array.shape[0], jpg_array.shape[1]))

        for i, path in enumerate(jpeg_paths):
            jpg_array = skimage.color.rgb2gray(imread(path))
            numpy.copyto(skimage_array[i], jpg_array)

        return SimpleITK.GetImageFromArray(skimage_array)

    axial_image = get_image_from_jpeg_paths(axial_image_paths)
    sagittal_image = get_image_from_jpeg_paths(sagittal_image_paths)

    all_series = []
    all_series.append(schema.ImageSeries(
        type=schema.ImageSeriesType.PATIENT.name,
        study=study,
        metadata_pickled=b'',
        image_pickled=pickle.dumps(axial_image),
        orientation=dicom_lib.Orientation.AXIAL.name))
    all_series.append(schema.ImageSeries(
        type=schema.ImageSeriesType.PATIENT.name,
        study=study,
        metadata_pickled=b'',
        image_pickled=pickle.dumps(sagittal_image),
        orientation=dicom_lib.Orientation.SAGITTAL.name))

    return all_series

def ImageSeriesFromNIFTIFiles(study):
    from lib import schema
    file_pattern = os.path.join(study.file_dir_path, '**', '*')
    paths = glob.glob(file_pattern, recursive=True)
    if len(paths) > 3000:
        logging.error(
                'Max. 3000 files per study. Found: {} paths in {}.'.format(
                    len(paths), study.file_dir_path))
        return []

    file_paths = [path for path in paths if os.path.isfile(path)]
    if not file_paths:
        raise FileNotFoundError('No files match pattern %s' % file_pattern)

    logging.info(
            'Processing %d files from %s' % (len(file_paths), file_pattern))

    axial_image = None
    sagittal_image = None

    reader = SimpleITK.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")

    ax_re = re.compile('.*ax.*\.nii')
    sag_re = re.compile('.*sag.*\.nii')
    for path in file_paths:
        filename = os.path.basename(path).lower()
        if not axial_image and ax_re.match(filename):
            reader.SetFileName(path)
            axial_image = reader.Execute();
        if not sagittal_image and sag_re.match(filename):
            reader.SetFileName(path)
            sagittal_image = reader.Execute();
        if axial_image and sagittal_image:
            break

    all_series = []

    if axial_image:
        all_series.append(schema.ImageSeries(
            type=schema.ImageSeriesType.PATIENT.name,
            study=study,
            metadata_pickled=b'',
            image_pickled=pickle.dumps(axial_image),
            orientation=dicom_lib.Orientation.AXIAL.name))
    else:
        logging.error(
                "No axial image found that mattched /{}/".format(ax_re.pattern))

    # if sagittal_image:
    #     all_series.append(schema.ImageSeries(
    #         type=schema.ImageSeriesType.PATIENT.name,
    #         study=study,
    #         metadata_pickled=b'',
    #         image_pickled=pickle.dumps(sagittal_image),
    #         orientation=dicom_lib.Orientation.SAGITTAL.name))
    # else:
    #     logging.error(
    #             "No sagittal image found that mattched /{}/".format(
    #                 sag_re.pattern))

    return all_series

class ImageSeriesMixin(object):
    """Represents the image and associated metadata from one patient series."""

    @property
    def metadatas(self):
        if not hasattr(self, '_metadatas'):
            if self.metadata_pickled:
                self._metadatas = pickle.loads(self.metadata_pickled)
            else:
                self._metadatas = None
        return self._metadatas

    @property
    def metadata(self):
        if self.metadatas:
            return self.metadatas[0]
        return None

    @property
    def image(self):
        if not hasattr(self, '_image'):
            self._image = pickle.loads(self.image_pickled)
        return self._image

    def to_dir(self, dir_path, file_type='png'):
        """Writes this PatientImageSeries to a directory.

        This generally writes:
            - image-001.png
            - image-002.png
            - ...

        This is useful for visually debugging series, and to make image assets
        available to the report HTML template in report_lib.

        Args:
            dir_path: (string) Path to directory to write files.
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        if file_type == 'png':
            util_lib.write_3d_image_as_slices(self.image, dir_path)
        elif file_type == 'nifti':
            util_lib.write_3d_image_as_slices(self.image, dir_path, file_suffix='.nii', image_io='NiftiImageIO')
        else:
            logging.error('Unrecognized file type: {}'.format(file_type))

    def get_pixel_area(self):
        """Returns the area represented by one pixel in mm^2."""
        pixel_spacing = self.metadata[0x00280030].value
        return pixel_spacing[0] * pixel_spacing[1]

    @property
    def series_uid(self):
        if self.metadata and 0x0020000E in self.metadata:
            return str(self.metadata[0x0020000E].value)
        return 'Unknown'

    def is_t2(self):
        if self.metadata and hasattr(self.metadata, 'SeriesDescription'):
            desc = self.metadata.SeriesDescription
            if 'T2' in desc.upper():
                return True
        return False

    def is_ir(self):
        if self.metadata and hasattr(self.metadata, 'ScanningSequence'):
            scanning_seq = self.metadata.ScanningSequence
            if isinstance(scanning_seq, str):
                if 'IR' in scanning_seq.upper():
                    return True
            else:
                for s in scanning_seq:
                    if 'IR' in s.upper():
                        return True
        return False

    def get_render_orientation(self):
        """Returns the viewing orientation of this DICOM series.

        Returns [left, right, top, bottom, back, front], where:

              up
        left      right
             down

        and 'back' is behind the current imagine and 'front' is through the
        current image.

        Key:
          L = left
          R = right
          A = anterior
          P = posterior
          T = top
          B = bottom

        eg. ['R', 'L', 'A', 'P', 'T', 'B']
        """
        orientation_lookup = {
                'x': ['R', 'L'],
                '-x': ['L', 'R'],
                'y': ['A', 'P'],
                '-y': ['P', 'A'],
                'z': ['B', 'T'],
                '-z': ['T', 'B'],
        }

        render_orientation = []
        orientation = self.get_orientation()
        if not orientation:
            return None

        for o in orientation:
            if o in orientation_lookup:
                render_orientation.extend(orientation_lookup[o])
            else:
                logging.error(
                        'Could not interpret orientation axis "{}"'.format(o))
                return None

        return render_orientation

    def get_orientation(self):
        """Returns the viewing orientation of this DICOM series.

        Returns [row, col, row x col], where:
          - row is the DICOM patient axis from left to right.
          - col is the DICOM patient axis from top to bottom.
          - row x col is the DICOM patient axis looking through the image.

        For example, ['x', '-z', 'y'] would be returned when looking at
        coronal slices of a patient standing straight up, facing the viewer.

        Returns None on error.
        """
        def get_axis(unit_vector):
            if len(unit_vector) > 3:
                logging.error('Expected length 3 unit vector.')
                return None

            max_val = 0
            max_index = 0
            for i, val in enumerate(unit_vector):
                if abs(val) > abs(max_val):
                    max_val = val
                    max_index = i

            if max_index > 2:
                logging.error('Unit vector index out of range')
                return None
            sign = ['x','y','z'][max_index]
            axis = ''
            if max_val < 0:
                axis = '-'

            return axis + sign

        if self.metadata:
            series_orientation = []
            img_orientation = self.metadata[0x00200037].value

            row_vector = numpy.asarray(img_orientation[:3])
            col_vector = numpy.asarray(img_orientation[3:])
            depth_vector = numpy.cross(row_vector, col_vector)

            for vector in [row_vector, col_vector, depth_vector]:
                series_orientation.append(get_axis(vector))

            return series_orientation

        return None

    def get_image_position(self, imgSlice=0):
        """Returns (0020, 0032) Image Position for the given slice."""
        try:
            return list(self.metadatas[imgSlice][0x00200032].value)
        except (ValueError, KeyError, IndexError) as e:
            logging.error("Error handling DICOM metadata.", exc_info=True)
        return None

    def get_patient_coordinates(self, px_coordinates):
        """Converts from (slice, row, column) coordinates to patient coordinates.

        Args:
            px_coordinates: (float, float, float)) slice, row, col

        Returns:
            tuple(float, float, float) or None on error.
        """
        if not self.metadatas:
            logging.error(
                    'Attempted to get patient coordinates for series without '
                    'DICOM metadata.')
            return None

        try:
            if len(self.metadatas) == self.image.GetDepth():
                metadata_slice = px_coordinates[0]
            else:
                metadata_slice = 0

            # (0020, 0032) Image Position (Patient)
            output = numpy.asarray(
                    self.metadatas[metadata_slice][0x00200032].value)
            pixel_spacing = self.metadatas[metadata_slice][0x00280030].value
            img_orientation = self.metadatas[metadata_slice][0x00200037].value
            row_unit_vector = numpy.asarray(img_orientation[:3])
            row_unit_vector = row_unit_vector / numpy.linalg.norm(row_unit_vector)
            col_unit_vector = numpy.asarray(img_orientation[3:])
            col_unit_vector = col_unit_vector / numpy.linalg.norm(col_unit_vector)

            if len(self.metadatas) != self.image.GetDepth():
                slice_increment = float(self.metadata[0x00180088].value)
                slice_unit_vector = numpy.cross(row_unit_vector, col_unit_vector)
                output = numpy.add(
                        output, slice_unit_vector * slice_increment)

            # Offset the start position by the pixel coordinates.
            output = numpy.add(
                    output,
                    col_unit_vector * px_coordinates[1] * pixel_spacing[0])
            output = numpy.add(
                    output,
                    row_unit_vector * px_coordinates[2] * pixel_spacing[1])
            return output
        except (ValueError, KeyError, IndexError) as e:
            logging.error("Error handling DICOM metadata.", exc_info=True)
        return None

    def get_pixel_coordinates(self, patient_coords, round_decimals=2):
        """Convert patient coordinates to pixel coordinates.

        Args:
            patient_coords: (int, int, int) x, y, z of in patient coordinates.
            round_decimals: (int) Number of decimals to round to.

        Returns:
            (int, float, float) slice, pixel, pixel
        """
        if not self.metadatas:
            logging.error(
                    'Attempted to get pixel coordinates for series without '
                    'DICOM metadata.')
            return None

        try:
            # Break down <x, y, z> into sum of 3 unit vectors based on
            # (0020,0037) Image Orientaiton (Patient).
            #
            # TODO(billy): We assume the Image Orientation, Pixel Spacing,
            # and Spacing Between Slices for each slice is identical. To
            # increase robustness, we should use the metadata of each
            # slice (when available) instead of inferring these values from
            # the base slice.
            img_orientation = self.metadata[0x00200037].value
            row_unit_vector = numpy.asarray(img_orientation[:3])
            row_unit_vector = row_unit_vector / numpy.linalg.norm(row_unit_vector)
            col_unit_vector = numpy.asarray(img_orientation[3:])
            col_unit_vector = col_unit_vector / numpy.linalg.norm(col_unit_vector)
            depth_unit_vector = numpy.cross(row_unit_vector, col_unit_vector)
            slice_increment = float(self.metadata[0x00180088].value)

            # Adjust vectors by pixel spacing.
            depth_unit_vector =  depth_unit_vector * slice_increment
            pixel_spacing = self.metadata[0x00280030].value
            row_unit_vector = row_unit_vector * pixel_spacing[1]
            col_unit_vector = col_unit_vector * pixel_spacing[0]

            # Solve system of linear equations.
            coeff_matrix = numpy.column_stack((depth_unit_vector,
                                               col_unit_vector,
                                               row_unit_vector))
            # (0020, 0032) Image Position (Patient)
            relative_position = (numpy.asarray(patient_coords) -
                                 numpy.asarray(self.metadata[0x00200032].value))
            unit_weights = numpy.linalg.solve(coeff_matrix, relative_position)
            unit_weights = numpy.around(unit_weights, decimals = round_decimals)

            return unit_weights

        except (ValueError, KeyError, IndexError) as e:
            logging.error("Error handling DICOM metadata.", exc_info=True)
        return None
