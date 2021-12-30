"""Library for representing DICOM studies and images."""

from collections import defaultdict
import copy
import datetime
from enum import IntEnum, auto
import glob
import json
import logging
import os
import pickle
import re
import sys
from shutil import copyfile
import tempfile
import zipfile

import checksumdir
from pony import orm
import SimpleITK

from lib import classifier_lib
from lib import dicom_lib
from lib import series_lib
from lib import segmentation_lib
from lib import util_lib


def CreateStudy(input_dir, name=None):
    from lib import schema

    input_dir = os.path.abspath(input_dir)
    study_name=os.path.basename(input_dir)
    if name:
        study_name = name

    study = schema.Study(
            name=study_name,
            file_dir_path=input_dir,
            file_dir_checksum=checksumdir.dirhash(input_dir, 'md5'))

    try:
        patient_series = series_lib.ImageSeriesFromDICOMFiles(study)
    except RuntimeError:
        patient_series = None
        logging.error('Could not parse DICOM files for {}.'.format(input_dir))
    if patient_series:
        study.set_metadata_from_series(patient_series[0])
        for series in patient_series:
            study.image_series.add(series)
        study.image_file_type = schema.ImageFileType.DICOM.name
        return study

    logging.info('No DICOM series found.. attempting to interpret as NIFTI.')
    nifti_series = series_lib.ImageSeriesFromNIFTIFiles(study)
    if nifti_series:
        for series in nifti_series:
            study.image_series.add(nifti_series)
        study.image_file_type = schema.ImageFileType.NIFTI.name
        return study

    logging.info('No NIFTI series found.. attempting to interpet as JPG.')
    jpeg_series = series_lib.ImageSeriesFromJPEGFiles(study)
    if jpeg_series:
        for series in jpeg_series:
            study.image_series.add(jpeg_series)
        study.image_file_type = schema.ImageFileType.JPEG.name
        return study

    orm.rollback()
    raise ValueError('No valid image series found in {}'.format(input_dir))


class StudyMixin(object):
    """Study represents one patient study, containing one or more series.

    See
    https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction
    for more information.
    """
    def set_metadata_from_series(self, series):
        """
        Args:
            series: (schema.ImageSeries)
        """
        metadata = series.metadata
        if metadata:
            # (0008, 0050) Accession Number
            if 0x00080050 in metadata:
                self.accession_number = str(metadata[0x00080050].value)
            # (0020, 000D) Study Instance UID
            if 0x0020000D in metadata:
                self.study_instance_uid = str(metadata[0x0020000D].value)
            # (0010, 0010) Patient's Name
            if 0x00100010 in metadata:
                self.patient_name = str(metadata[0x00100010].value)
            # (0010, 1010) Patient's Age
            if 0x00101010 in metadata:
                self.patient_age = str(metadata[0x00101010].value)
            # (0010, 1020) Patient's Size
            if 0x00101020 in metadata:
                self.patient_size = str(metadata[0x00101020].value)
            # (0010, 0040) Patient's Sex
            if 0x00100040 in metadata:
                self.patient_sex = str(metadata[0x00100040].value)


