"""Library for abstracting models that operate on Studies."""

from datetime import datetime
from enum import Enum
import logging
import os
from pathlib import Path
import pickle

from config2.config import config
import cv2
import numpy
from PIL import Image
from pony import orm
import SimpleITK
import skimage.transform

from xsegment.models import segment

from lib import dicom_lib
from lib import img_lib
from lib import segmentation_lib
from lib import series_lib

from lib import schema

CLASSIFICATION_VERSION = "20210804"

CANAL_160_WEIGHTS_FILE = os.path.join(Path().absolute(), 'bin/models/canal/UNet160.hdf5')
CANAL_256_WEIGHTS_FILE = os.path.join(Path().absolute(), 'bin/models/canal/UNet256.hdf5')
DISK_WEIGHTS_FILE = os.path.join(Path().absolute(), 'bin/models/disk/UNet.hdf5')
FORAMEN_WEIGHTS_FILE = os.path.join(Path().absolute(), 'bin/models/foramen/UNet.hdf5')

AXIAL_HISTOGRAM_TEMPLATE = os.path.join(Path().absolute(), 'bin/histogram_templates/template_axial.nii.gz')
SAGITTAL_HISTOGRAM_TEMPLATE = os.path.join(Path().absolute(), 'bin/histogram_templates/template_sagittal.nii.gz')


def get_configured_classifers():
    canal_classifier = None
    if config.spineai.classification.canal.engine == 'bilwaj':
        canal_classifier = DefaultCanalClassifier
    elif config.spineai.classification.canal.engine == 'xsegment':
        canal_classifier = DefaultCanalXClassifier
    else:
        raise ValueError(
                'Unrecognized canal classifier engine: %s',
                config.spineai.classification.canal.engine)

    disk_classifier = None
    if config.spineai.classification.disc.engine == 'bilwaj':
        disk_classifier = DefaultDiskClassifier
    else:
        raise ValueError(
                'Unrecognized disc classifier engine: %s',
                config.spineai.classification.disc.engine)

    foramen_classifier = None
    if config.spineai.classification.foramen.engine == 'bilwaj':
        foramen_classifier = DefaultForamenClassifier
    else:
        raise ValueError(
                'Unrecognized foramen classifier engine: %s',
                config.spineai.classification.foramen.engine)

    return {
            schema.ClassificationType.CANAL: canal_classifier,
            schema.ClassificationType.DISK: disk_classifier,
            schema.ClassificationType.FORAMEN: foramen_classifier
    }


@orm.db_session
def generate_default_classifications(study):
    """Creates a Classification for each type.

    This method selects the best series from study.series(type="PATIENT") for
    each input type, and returns a Classification for each one.

    Args:
        study: (schema.Study)

    Returns:
        list(Classifications)
    """
    db_study = orm.select(s for s in schema.Study if s.id == study.id)[:]
    if not study:
        logging.error(
                'generate_classification: No Study with id "{}". '
                'Skipping...'.format(study_id))
        return
    db_study = db_study[0]

    # TODO(billy): Add configuration system to choose Classifier or XClassifier.
    classifiers = get_configured_classifers()
    classifications = []

    for c_type in classifiers:
        series = classifiers[c_type].sorted_by_fit(study.patient_series)[0]

        classifications.append(schema.Classification(
                study=db_study,
                type=c_type.name,
                input_series=series))

    return classifications


def get_default_registry():
    registry = ClassifierRegistry()

    classifiers = get_configured_classifers()
    logging.info('Default classifiers: %s', classifiers)
    for c_type in classifiers:
        registry.register_classifier(c_type, classifiers[c_type]())

    return registry


class ClassificationMixin(object):
    """Encapsulates the inputs, outputs, and metadata for a classification job.
    """

    def __init__(self, classification_input):
        self.input = classification_input
        self.outputs = []

    def to_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        input_path = os.path.join(dir_path, 'input')
        self.input.to_dir(input_path)

        outputs_path = os.path.join(dir_path, 'outputs')
        for output in self.outputs:
            output.to_dir(os.path.join(outputs_path, output.type.name))


class ClassifierRegistry(object):
    """Processes Classifications with registered Classifiers."""

    def __init__(self):
        self._registered_classifiers = {}

    def register_classifier(self, classification_type, classifier):
        """
        Args:
            classification_type: (schema.ClassificationType)
            classifier: (Classifier)
        """
        self._registered_classifiers[classification_type] = classifier

    def process(self, classification):
        """
        Args:
            classification: (schema.Classification)
        """
        ctype = schema.ClassificationType[classification.type]
        if ctype not in self._registered_classifiers:
            raise ValueError(
                    'No registered Classifier for ClassificationType '
                    '"{}".'.format(ctype.name))

        classifier = self._registered_classifiers[ctype]
        study = classification.study
        classifier.classify(classification, study)


class Classifier(object):
    """Defines the interface of a Classifier.

    A Classifier consumes a Classification specificiation and the Study on
    which to operate on.

    This class is primarily used by ClassifierRegistry to organize
    available classification types. (eg. canal, disk, etc.)
    """

    def classify(self, classification, full_study):
        """Perform classification on given input.

        Args:
            classification: (schema.Classification)
            full_study: (schema.Study) Existing loaded full Study to classify.
                full_study.id must match classification.study.id.
        """
        raise NotImplementedError()


class KerasImageClassifier(Classifier):
    """A Classifier based on Bilwaj Gaonkar's (UCLA) code.

    This classifier is intended to injest Keras models. See models.bilwaj_lib
    for more details.

    Models are registered to self.models, and the results are unified with
    self.join_output_with to produce the final output.
    """

    def __init__(self):
        self.join_output_with = numpy.logical_or
        self.preprocess_settings = {
            'n4_bias_correction': False,
            'histomatch': True,
            'histomatch_template_path': '',
            'invert': False,
            'resize': (256, 256),
        }
        self.classify_settings = {
            # If true, resize the output mask to input image.
            'preserve_image_size': False,
        }

    @property
    def models(self):
        if not hasattr(self, '_models'):
            self._models = []
        return self._models

    @staticmethod
    def sorted_by_fit(series):
        """Sorts series by descending fit for image classification.

        Args:
            series: list(series_lib.ImageSeries)

        Returns:
            list(series_lib.ImageSeries)
        """
        # NOTE(billy): Note that due to the nature of sorting the highest
        # priority/most important critera are listed last in code.

        # Prefer series with a larger number of slices.
        series = sorted(series, key=lambda s: s.image.GetDepth(), reverse=True)

        # Prefer non-IR series.
        series = sorted(series, key=lambda s: s.is_ir())

        # Prefer T2 series.
        series = sorted(series, key=lambda s: s.is_t2(), reverse=True)

        return series

    def preprocess_image(self, image, original_metadatas):
        """
        Returns:
            (SimpleITK.Image, list([float, float])) New image and pixel_spacing.
        """
        from lib import bilwaj_lib
        new_image = SimpleITK.Image(image)
        if self.preprocess_settings['n4_bias_correction']:
            new_image = img_lib.n4_bias_field_correction(new_image)

        if self.preprocess_settings['histomatch']:
            if not self.preprocess_settings['histomatch_template_path']:
                logging.error(
                        'Histomatch requested but histomatch_template_path not '
                        'initialized.')
            else:
                template_image = SimpleITK.ReadImage(
                        self.preprocess_settings['histomatch_template_path'],
                        image.GetPixelID())
                new_image = img_lib.histomatch(new_image, template_image)

        if self.preprocess_settings['invert']:
            new_image = img_lib.invert(new_image)

        new_image = img_lib.normalize(new_image)

        if self.preprocess_settings['resize']:
            new_image = img_lib.resize(new_image, self.preprocess_settings['resize'])

        # Correct for new pixel spacing after resize.
        image_array = SimpleITK.GetArrayFromImage(image)
        new_pixel_spacings = []
        if original_metadatas:
            for metadata in original_metadatas:
                orig_pixel_spacing = metadata[0x00280030].value

                new_size = (image.GetHeight(), image.GetWidth())
                if self.preprocess_settings['resize']:
                    new_size = self.preprocess_settings['resize']

                new_row_spacing = orig_pixel_spacing[0] * image_array.shape[1] / new_size[0]
                new_col_spacing = orig_pixel_spacing[1] * image_array.shape[2] / new_size[1]
                new_pixel_spacings.append([new_row_spacing, new_col_spacing])

        return (new_image, new_pixel_spacings)

    def classify_image(self, patient_image, preprocessed_image):
        """Performs classification on given ImageSeriesMixin.

        Args:
            patient_image : (SimpleITK.Image)
            preprocessed_image: (SimpleITK.Image)

        Returns:
            (SimpleITK.Image)
        """
        from lib import bilwaj_lib
        img_array = SimpleITK.GetArrayFromImage(preprocessed_image)
        # TODO(billy): Check this assumption.
        num_images = img_array.shape[0]

        out_arrays = []
        for model in self.models:
            patches = list()

            # TODO(billy): Check this assumption. Requires understanding
            # Bilwaj's code better.
            patch_shape = model.input_shape[1:]
            if patch_shape[0] != patch_shape[1]:
                logging.error(
                        "Only square patches are currently supported. "
                        "(got: {})".format(str(patch_shape)))
            patch_size = patch_shape[0]

            for i in range(num_images):
                patch = bilwaj_lib.segment_patch(img_array[i,:,:], model, patch_size)
                patches.append(patch)

            out_arrays.append(numpy.stack(patches))

        # TODO(billy): Make this configurable.
        classification_threshold = 0.01
        out_array = None
        if self.classify_settings['preserve_image_size']:
            original_image_size = patient_image.GetSize()
            output_numpy_size = (
                    img_array.shape[0],
                    original_image_size[0],
                    original_image_size[1])
            out_array = numpy.full(output_numpy_size, False)
            for i, array in enumerate(out_arrays):
                out_arrays[i] = skimage.transform.resize(array, output_numpy_size)
            for array in out_arrays:
                out_array = numpy.logical_or(out_array, (array > classification_threshold))
        else:
            out_array = numpy.full(img_array.shape, False)
            for array in out_arrays:
                out_array = numpy.logical_or(out_array, (array > classification_threshold))

        out_image = SimpleITK.GetImageFromArray(out_array.astype('float32'))

        if self.classify_settings['preserve_image_size']:
            original_image_size = patient_image.GetSize()
            resized_img = img_lib.resize(preprocessed_image, (original_image_size[0], original_image_size[1]), interpolation=cv2.INTER_LINEAR)
            out_image.CopyInformation(resized_img)
        else:
            out_image.CopyInformation(preprocessed_image)

        return out_image

    def get_segmentation_class(self):
        raise NotImplementedError()

    def get_segmentation_type(self):
        """Get the str name of the schema.SegmentationType for this Classifier.

        Returns:
            (str)
        """
        raise NotImplementedError()

    def classify(self, classification, full_study):
        patient_series = classification.input_series

        db_study = orm.select(
                s for s in schema.Study if s.id == full_study.id)[:][0]

        metadata_pickled = patient_series.metadata_pickled
        if patient_series.metadata_pickled:
            metadatas = pickle.loads(patient_series.metadata_pickled)
            (preprocessed_image, new_spacings)  = self.preprocess_image(patient_series.image, metadatas)
            for i, metadata in enumerate(metadatas):
                metadata[0x00280030].value = new_spacings[i]
            metadata_pickled = pickle.dumps(metadatas)
        else:
            (preprocessed_image, _) = self.preprocess_image(patient_series.image, None)

        preprocessed_patient_series = schema.ImageSeries(
                type=schema.ImageSeriesType.PREPROCESSED.name,
                study=full_study,
                image_pickled=pickle.dumps(preprocessed_image),
                metadata_pickled=metadata_pickled)

        seg_image = self.classify_image(
                patient_series.image, preprocessed_patient_series.image)
        seg_series = schema.ImageSeries(
                type=schema.ImageSeriesType.RAW.name,
                study=full_study,
                image_pickled=pickle.dumps(seg_image),
                metadata_pickled=metadata_pickled)

        postprocessed_img = self.get_segmentation_class().postprocess(seg_image)

        postprocessed_segmentation_series = schema.ImageSeries(
                type=schema.ImageSeriesType.POSTPROCESSED.name,
                study=full_study,
                image_pickled=pickle.dumps(postprocessed_img),
                metadata_pickled=metadata_pickled)

        segmentation_db = schema.Segmentation(
                study=db_study,
                classification=classification,
                type=self.get_segmentation_type(),
                creation_datetime=datetime.now(),
                preprocessed_patient_series=preprocessed_patient_series,
                raw_segmentation_series=seg_series,
                postprocessed_segmentation_series=postprocessed_segmentation_series)

        return segmentation_db


class DefaultCanalClassifier(KerasImageClassifier):

    def __init__(self):
        from lib import bilwaj_lib
        super().__init__()

        self.preprocess_settings['histomatch_template_path'] = (
                AXIAL_HISTOGRAM_TEMPLATE)

        model_160 = bilwaj_lib.get_canal_model({'img_shape': (160, 160, 1)})
        model_160.load_weights(CANAL_160_WEIGHTS_FILE)
        self.models.append(model_160)

        model_256 = bilwaj_lib.get_canal_model({
            'img_shape': (256, 256, 1),
            'start_ch': 16,
            'residual': False,
        })
        model_256.load_weights(CANAL_256_WEIGHTS_FILE)
        self.models.append(model_256)

    @staticmethod
    def sorted_by_fit(series):
        series = KerasImageClassifier.sorted_by_fit(series)

        def valid_orientation(series):
            orientation = dicom_lib.get_orientation(series)
            return (orientation == dicom_lib.Orientation.AXIAL or
                    orientation == dicom_lib.Orientation.AXIAL_REVERSE)

        return sorted(series, key=valid_orientation, reverse=True)

    def get_segmentation_class(self):
        return segmentation_lib.CanalSegmentationMixin

    def get_segmentation_type(self):
        return schema.SegmentationType.CANAL.name


class DefaultDiskClassifier(KerasImageClassifier):

    def __init__(self):
        from lib import bilwaj_lib
        super().__init__()

        self.preprocess_settings['histomatch_template_path'] = (
                SAGITTAL_HISTOGRAM_TEMPLATE)

        model = bilwaj_lib.get_disk_model()
        model.load_weights(DISK_WEIGHTS_FILE)
        self.models.append(model)

    @staticmethod
    def sorted_by_fit(series):
        series = KerasImageClassifier.sorted_by_fit(series)

        def valid_orientation(series):
            orientation = dicom_lib.get_orientation(series)
            return (orientation == dicom_lib.Orientation.SAGITTAL or
                    orientation == dicom_lib.Orientation.SAGITTAL_REVERSE)

        return sorted(series, key=valid_orientation, reverse=True)

    def get_segmentation_class(self):
        return segmentation_lib.DiskSegmentationMixin

    def get_segmentation_type(self):
        return schema.SegmentationType.DISK.name


class DefaultForamenClassifier(KerasImageClassifier):

    def __init__(self):
        from lib import bilwaj_lib
        super().__init__()

        self.preprocess_settings['histomatch_template_path'] = (
                SAGITTAL_HISTOGRAM_TEMPLATE)

        model = bilwaj_lib.get_foramen_model()
        model.load_weights(FORAMEN_WEIGHTS_FILE)
        self.models.append(model)

    @staticmethod
    def sorted_by_fit(series):
        series = KerasImageClassifier.sorted_by_fit(series)

        def valid_orientation(series):
            orientation = dicom_lib.get_orientation(series)
            return (orientation == dicom_lib.Orientation.SAGITTAL or
                    orientation == dicom_lib.Orientation.SAGITTAL_REVERSE)

        return sorted(series, key=valid_orientation, reverse=True)

    def get_segmentation_class(self):
        return segmentation_lib.ForamenSegmentationMixin

    def get_segmentation_type(self):
        return schema.SegmentationType.FORAMEN.name


class XImageClassifier(Classifier):
    """A Classifier based on Marcus Karr's xsegmentor code."""

    def __init__(self):
        self.segmenter = segment.Segmenter()


    def get_segmentation_class(self):
        raise NotImplementedError

    def get_segmentation_type(self):
        raise NotImplementedError

    def classify_slice(self, pil_image):
        """Takes a Pillow image and returns the segmentation of that image."""
        return self.segmenter.segment(pil_image, resize_dim=None)

    def classify(self, classification, full_study):
        db_study = orm.select(
                s for s in schema.Study if s.id == full_study.id)[:][0]

        patient_series = classification.input_series

        sitk_image = patient_series.image

        keras_classifier = KerasImageClassifier()
        keras_classifier.preprocess_settings['histomatch'] = True
        keras_classifier.preprocess_settings['resize'] = (256, 256)
        keras_classifier.preprocess_settings['histomatch_template_path'] = (
                AXIAL_HISTOGRAM_TEMPLATE)
        metadatas = pickle.loads(patient_series.metadata_pickled)
        (preprocessed_image, new_spacings) = keras_classifier.preprocess_image(sitk_image, metadatas)
        for i, metadata in enumerate(metadatas):
            metadata[0x00280030].value = new_spacings[i]
        metadata_pickled = pickle.dumps(metadatas)

        preprocessed_patient_series = schema.ImageSeries(
                type=schema.ImageSeriesType.PREPROCESSED.name,
                study=db_study,
                image_pickled=pickle.dumps(preprocessed_image),
                metadata_pickled=metadata_pickled)

        img_array = SimpleITK.GetArrayFromImage(preprocessed_image)
        img_array = img_array / numpy.max(img_array) * 255
        img_array = numpy.uint8(img_array)

        segmented_array = numpy.zeros_like(img_array)

        for i in range(len(img_array)):
            pil_image = Image.fromarray(img_array[i])
            pil_image.save('/tmp/img.png')
            segmented = self.classify_slice(pil_image)
            segmented.save('/tmp/img2.png')
            segmented_array[i] = numpy.array(segmented)

        segmented_sitk_image = SimpleITK.GetImageFromArray(
                segmented_array)

        seg_series = schema.ImageSeries(
                type=schema.ImageSeriesType.RAW.name,
                study=db_study,
                image_pickled=pickle.dumps(segmented_sitk_image),
                metadata_pickled=metadata_pickled)

        postprocessed_img = self.get_segmentation_class().postprocess(segmented_sitk_image)

        postprocessed_segmentation_series = schema.ImageSeries(
                type=schema.ImageSeriesType.POSTPROCESSED.name,
                study=db_study,
                image_pickled=pickle.dumps(postprocessed_img),
                metadata_pickled=metadata_pickled)

        segmentation_db = schema.Segmentation(
                study=db_study,
                classification=classification,
                type=self.get_segmentation_type(),
                creation_datetime=datetime.now(),
                preprocessed_patient_series=preprocessed_patient_series,
                raw_segmentation_series=seg_series,
                postprocessed_segmentation_series=postprocessed_segmentation_series)

        return segmentation_db

class DefaultCanalXClassifier(XImageClassifier):

    def __init__(self, *args, **kwargs):
        super().__init__()

    def sorted_by_fit(series):
        return DefaultCanalClassifier.sorted_by_fit(series)

    def get_segmentation_class(self):
        return segmentation_lib.CanalSegmentationMixin

    def get_segmentation_type(self):
        return schema.SegmentationType.CANAL.name
