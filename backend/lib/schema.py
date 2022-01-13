"""Definitions for the SpineAI Database schema."""

import base64
from datetime import datetime
from enum import Enum
import io
import logging
import numpy
import pickle
import png
import uuid

from pony.orm import *
import pydicom
import SimpleITK

from lib import dicom_lib
from lib import img_lib
from lib.classifier_lib import ClassificationMixin, CLASSIFICATION_VERSION
from lib.series_lib import ImageSeriesMixin
from lib.segmentation_lib import (
        CanalSegmentationMixin,
        DiskSegmentationMixin,
        SegmentationMixin)
from lib.report_lib import ReportMixin
from lib.study_lib import StudyMixin


db = Database()


def get_uuid():
    return str(uuid.uuid4())


class EventState(Enum):
    """States for tables that are listened on and processed later.

    See runtime/database_listener.py.
    """
    NEW = 'NEW'
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    PROCESSED = 'PROCESSED'
    ERROR = 'ERROR'

class EventMixin(object):
    """Mixin for database objects that can be listened on.

    See runtime/database_listener.py.

    NOTE(billy): We don't use true inheritance due how Pony handles inheritance
    representation in the underlying database. Pony represents all objects in
    one child database. We would prefer that each child has its own table.
    See https://docs.ponyorm.org/entities.html#representing-inheritance-in-the-database
    for more information.
    """

    @classmethod
    def get_unprocessed(cls):
        """Returns Query object for events considered "unprocessed"."""
        return cls.select(
                lambda obj: obj.state in [
                    EventState.NEW.name,
                    EventState.QUEUED.name,
                    EventState.PROCESSING.name])


class IngestionType(Enum):
    DICOM_FETCH = 'DICOM_FETCH'
    FILE_BYTES = 'FILE_BYTES'


class Ingestion(db.Entity, EventMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    # Event attributes
    # TODO(billy): Abstract these attributes.
    state = Required(str, default=EventState.NEW.name)
    started_datetime = Optional(datetime)
    completed_datetime = Optional(datetime)
    error_str = Optional(str)

    type = Optional(str, default=IngestionType.FILE_BYTES.name)
    name = Optional(str)

    # type == "DICOM_FETCH"
    # TODO(billy): Consider serializing/unserializing a pydicom.DataSet to allow
    # for arbitrary DICOM Q/R.
    accession_number = Optional(str)

    # type == "FILE_BYTES"
    file_archive_bytes = Optional(bytes)


class PatientSex(Enum):
    UNKNOWN = 'UNKNOWN'
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class ImageFileType(Enum):
    DICOM = 'DICOM'
    NIFTI = 'NIFTI'
    JPEG = 'JPEG'


class Study(db.Entity, StudyMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)

    creation_datetime = Required(datetime, default=datetime.now)

    name = Required(str)
    file_dir_path = Required(str)
    file_dir_checksum = Required(str)

    # IMAGE_FILE_TYPE
    image_file_type = Optional(str)

    # NOTE(billy): The following attributes are set by DICOM metadata during
    # ingestion. Re-setting them should keep them comformed to DICOM values.
    accession_number = Optional(str)
    patient_age = Optional(str)
    patient_name = Optional(str)
    patient_size = Optional(str)
    patient_sex = Optional(str)
    study_instance_uid = Optional(str, index=True)

    #added new fields for patient
    mrn = Required(str)
    email = Required(str)
    date_of_birth = Required(datetime)
    phone_number = Required(int)
    diagnosis = Required(str)
    created_by = Optional(bool, default=False)

    classifications = Set('Classification')
    segmentations = Set('Segmentation')
    canal_segmentations = Set('CanalSegmentation')
    disk_segmentations = Set('DiskSegmentation')
    image_series = Set('ImageSeries')

    reports = Set('Report')
    action = Set('Action')

    @property
    def patient_series(self):
        return self.image_series.select(
                lambda series: series.type == ImageSeriesType.PATIENT.name)[:]

    @property
    def patient_age_years(self):
        return dicom_lib.age_string_to_years(self.patient_age)

    @property
    def patient_height_inches(self):
        if not self.patient_size:
            return None
        inches_in_meter = 39.3701
        return pydicom.valuerep.DSfloat(self.patient_size).real * inches_in_meter

    @property
    def patient_sex_enum(self):
        """
        Returns:
            (enum PatientSex)
        """
        if self.patient_sex == 'M':
            return PatientSex.MALE
        elif self.patient_sex == 'F':
            return PatientSex.FEMALE
        elif self.patient_sex == 'O':
            return PatientSex.OTHER
        return PatientSex.UNKNOWN


class ClassificationType(Enum):
    CANAL = 'CANAL'
    DISK = 'DISK'
    FORAMEN = 'FORAMEN'


class Classification(db.Entity, EventMixin, ClassificationMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    # Event attributes
    # TODO(billy): Abstract these attributes.
    state = Required(str, default=EventState.NEW.name)
    version = Required(str, default=CLASSIFICATION_VERSION)
    started_datetime = Optional(datetime)
    completed_datetime = Optional(datetime)
    error_str = Optional(str)

    study = Required(Study)
    type = Required(str)
    input_series = Required('ImageSeries')

    output_segmentations = Set('Segmentation')

    reports = Set('Report')


class SegmentationType(Enum):
    CANAL = 'CANAL'
    DISK = 'DISK'
    FORAMEN = 'FORAMEN'


class Segmentation(db.Entity, SegmentationMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    study = Required(Study)
    classification = Required(Classification)
    type = Required(str)

    preprocessed_patient_series = Required(
            'ImageSeries', reverse='preprocessed_segmentation')
    raw_segmentation_series = Required(
            'ImageSeries', reverse='raw_segmentation')
    postprocessed_segmentation_series = Required(
            'ImageSeries', reverse='postprocessed_segmentation')

    canal_segmentation = Optional('CanalSegmentation')
    disk_segmentation = Optional('DiskSegmentation')

    def __init__(self, *args, **kwargs):
        db.Entity.__init__(self, *args, **kwargs)

        if self.type == SegmentationType.CANAL.name:
            if not self.canal_segmentation:
                self.canal_segmentation = CanalSegmentation(
                        segmentation=self,
                        study=self.study)
        elif self.type == SegmentationType.DISK.name:
            if not self.disk_segmentation:
                self.disk_segmentation = DiskSegmentation(
                        segmentation=self,
                        study=self.study)


class CanalSegmentation(db.Entity, CanalSegmentationMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    segmentation = Required(Segmentation)
    study = Required(Study)

    num_slices = Optional(int)
    canal_areas = Optional(Json)

    def __init__(self, *args, **kwargs):
        db.Entity.__init__(self, *args, **kwargs)

        # TODO(billy): Make these metadata fields Required, and set with
        # a default function.
        self.num_slices = self.get_num_slices()
        self.canal_areas = self.get_all_canal_areas()


class DiskSegmentation(db.Entity, DiskSegmentationMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    segmentation = Required(Segmentation)
    study = Required(Study)


class ImageSeriesType(Enum):
    PATIENT = 'PATIENT'
    RAW = 'RAW'
    PREPROCESSED = 'PREPROCESSED'
    POSTPROCESSED= 'POSTPROCESSED'


class ImageSeries(db.Entity, ImageSeriesMixin):
    # Create Images upon intialization of ImageSeries.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # Convert all slices into Images and associate them with this
        # Imageseries.
        def slice_to_png_base64(array):
            # Normalize array to int16
            if (numpy.max(array) == 0):
                array = numpy.zeros_like(array, dtype=numpy.uint16)
            else:
                array = (array / numpy.max(array) *
                        numpy.iinfo(numpy.uint16).max).astype(numpy.uint16)

            png_raw = io.BytesIO()

            # TODO(billy): Improve this hack.
            # If there are only two values in the array (ie. black/white), then
            # we assume this is a segmentation and produce a transparency
            # suitable for web rendering.
            if len(numpy.unique(array)) <= 2:
                pil_img = img_lib.array_slice_to_PIL(array, True)
                pil_img.save(png_raw, format="PNG")
            else:
                png_obj = png.from_array(array, mode='L').write(png_raw)

            png_base64 = base64.b64encode(png_raw.getvalue())

            if not png_base64:
                study_name = self.study.name
                logging.warn(
                        'Empty PNG data from slice in study "%s"', study_name)
            return png_base64.decode('ascii')

        sitk_image = pickle.loads(self.image_pickled)
        sitk_array = SimpleITK.GetArrayFromImage(sitk_image)
        depth = sitk_image.GetDepth()
        if depth:  # 3D images
            for i, array in enumerate(sitk_array):
                b64_str = slice_to_png_base64(array)
                img = Image(
                        image_series=self,
                        slice=i,
                        total_slices=depth,
                        png_base64_str=b64_str)
        else:  # 2D images
            b64_str = slice_to_png_base64(sitk_array)
            img = Image(
                    image_series=self,
                    slice=1,
                    total_slices=1,
                    png_base64_str=b64_str)

    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    type = Required(str)
    study = Required(Study)

    # dicom_lib.Orientation
    orientation = Optional(str)

    classification = Set(Classification)
    preprocessed_segmentation = Optional(
            Segmentation, reverse='preprocessed_patient_series')
    raw_segmentation = Optional(
            Segmentation, reverse='raw_segmentation_series')
    postprocessed_segmentation = Optional(
            Segmentation, reverse='postprocessed_segmentation_series')

    image_pickled = Required(bytes)
    metadata_pickled = Required(bytes)

    images = Set('Image')


class Image(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    image_series = Required(ImageSeries, index=True)
    # 1-indexed slice.
    slice = Required(int)
    total_slices = Optional(int)

    png_base64_str = Required(str)


class ReportType(Enum):
    HTML_VIEWER = 'HTML_VIEWER'
    PDF_SIMPLE = 'PDF_SIMPLE'
    JSON = 'JSON'


class Report(db.Entity, EventMixin, ReportMixin):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    type = Required(str)
    creation_datetime = Required(datetime, default=datetime.now)

    # Event attributes
    # TODO(billy): Abstract these attributes.
    state = Required(str, default=EventState.NEW.name)
    started_datetime = Optional(datetime)
    completed_datetime = Optional(datetime)
    error_str = Optional(str)

    input_studies = Set(Study)
    input_classifications = Set(Classification)

    version = Optional(str)
    report_bytes = Optional(bytes)

    # Metadata for PDF_SIMPLE
    num_narrow_slices = Optional(int)
    surgery_recommended = Optional(bool)

class ApiLog(db.Entity):
    id = PrimaryKey(int, auto=True)
    uuid = Required(str, index=True, default=get_uuid)
    creation_datetime = Required(datetime, default=datetime.now)

    user = Optional(str)
    user_ip = Optional(str)
    action = Optional(str)
    api_url = Optional(str)
    object_type = Optional(str)
    object_id = Optional(str)
    object_uuid = Optional(str)


class Action(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    creation_datetime = Required(datetime, default=datetime.now)
    study = Required(Study)

