"""Helper libaries for working with DICOM images."""

import ast
import logging

from enum import Enum

# TODO(billy): Consider making these members of study_lib.py
# TODO(billy): Unit tests and sanity checks for these functions.

def age_string_to_years(dicom_age_string):
    """Converts DICOM Age String (AS) to float year value.

    See:
    http://dicom.nema.org/dicom/2013/output/chtml/part05/sect_6.2.html
    for more information.

    Args:
        dicom_age_string: (str) DICOM Age String. nnnD, nnnW, nnnM, or nnnY.
            (eg. "018M")

    Returns:
        (float) Age string or None
    """
    if not dicom_age_string:
        return None

    try:
        coeff = int(dicom_age_string[:3])
        if dicom_age_string[3] == 'D':
            return coeff/365.0
        elif dicom_age_string[3] == 'W':
            return coeff/52.0
        elif dicom_age_string[3] == 'M':
            return coeff/12.0
        elif dicom_age_string[3] == 'Y':
            return coeff
    except Exception as e:
        logging.error('Could not interpret "{}" as DICOM Age String.'.format(
            dicom_age_string))
        return None
    return None

class Orientation(Enum):
    """Represents the image orientation of a lumbar MRI series.

    AXIAL, SAGITTAL, and CORONAL are increasing with respect to the DICOM RCS.

    AXIAL => "top-down", increasing towards the head.
    SAGITTAL => "left-right", increasing towards patient's left.
    CORONAL => "front-back", increasing towards patenti's posterior.

    TODO(billy): Handle images rotated 180 degrees.
    """
    UNKNOWN = 'UNKNOWN'
    AXIAL = 'AXIAL'
    AXIAL_REVERSE = 'AXIAL_REVERSE'
    SAGITTAL = 'SAGITTAL'
    SAGITTAL_REVERSE = 'SAGITTAL_REVERSE'
    CORONAL = 'CORONAL'
    CORONAL_REVERSE = 'CORONAL_REVERSE'

def get_orientation_cosines(series):
    """Returns the cosines for the image orientation of the given series.

    Reads from (0020,0037), Image Orientation (Patient).

    See:
    http://dicomiseasy.blogspot.com/2013/06/getting-oriented-using-image-plane.html
    for more information.

    Args:
        series: (lib.series_lib.ImageSeriesMixin)

    Returns:
        list(float) 6 cosines from (0020,0037) of DICOM metadata or None on
            error.
    """
    ds = series.metadata
    if ds and hasattr(ds, 'ImageOrientationPatient'):
        orientation_str = str(ds.ImageOrientationPatient)
    else:
        return None

    if not orientation_str:
        logging.error('No image orientation (0020,0037) information in DICOM tags.')
        return None

    try:
        cosines = ast.literal_eval(orientation_str)
    except ValueError:
        logging.error(
                'Could not parse Image Orientation (0020,0037) as python '
                'expression. got: "%s"' % orientation_str)
        return None

    try:
        num_cosines = len(cosines)
    except TypeError:
        logging.error(
                'Could get length of Image Orientation (0020, 0037). '
                'got "%s".' % cosines)
        return None

    if num_cosines != 6:
        logging.error(
                'Image Orientation (0020, 0037) does not have 6 entries.'
                'got "%s".' % cosines)
        return None

    try:
        cosines = [float(c) for c in cosines]
    except ValueError:
        logging.error(
                'Could not parse Image Orientation (0020, 0037) as floats. '
                'got "%s".' % cosines)

    return cosines


def get_orientation(series):
    """Returns the orientation of the given image.

    Reads from (0020,0037), Image Orientation (Patient).

    Args:
        series: (series_lib.ImageSeriesMixin)

    Returns:
        (Orientation): Orientation of the image or Orientation.UNKNOWN on error.
    """
    if series.orientation:
        return Orientation(series.orientation)

    cosines = get_orientation_cosines(series)
    if not cosines:
        logging.error(
                'Could not get cosines from Image Orientation (0020, 0037).')
        return Orientation.UNKNOWN

    cos_45 = 0.707
    def get_alignment(cos):
        if cos > cos_45:
            return 1
        elif cos < -cos_45:
            return -1
        return 0

    # alignemnt = [Xx, Xy, Xz, Yx, Yy, Yz]
    alignment = [get_alignment(cos) for cos in cosines]

    if (alignment == [1, 0, 0, 0, 1, 0] or
        alignment == [-1, 0, 0, 0, -1, 0]):
        return Orientation.AXIAL
    elif (alignment == [-1, 0, 0, 0, 1, 0] or
          alignment == [1, 0, 0, 0, -1, 0]):
        return Orientation.AXIAL_REVERSE
    elif (alignment == [0, 1, 0, 0, 0, 1] or 
          alignment == [0, -1, 0, 0, 0, -1]):
        return Orientation.SAGITTAL
    elif (alignment == [0, 1, 0, 0, 0, -1] or 
          alignment == [0, -1, 0, 0, 0, 1]):
        return Orientation.SAGITTAL_REVERSE
    elif (alignment == [1, 0, 0, 0, 0, -1] or 
          alignment == [-1, 0, 0, 0, 0, 1]):
        return Orientation.CORONAL
    elif (alignment == [1, 0, 0, 0, 0, 1] or 
          alignment == [-1, 0, 0, 0, 0, -1]):
        return Orientation.CORONAL_REVERSE
    else:
        logging.warn(
                'Could not get orientation for DICOM image. got: %s' %
                str(cosines))
        return Orientation.UNKNOWN
