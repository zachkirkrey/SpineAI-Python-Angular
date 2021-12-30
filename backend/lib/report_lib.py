"""Library to generate a PDF report from a study."""
import copy
from datetime import datetime
from distutils.dir_util import copy_tree
import glob
import json
import logging
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from jinja2 import Environment
import jsonschema
from pony import orm
import pdfkit
import SimpleITK
import webpage2html

from lib import classifier_lib
from lib import clinical_lib
from lib import constants_lib
from lib import dicom_lib
from lib import img_lib
from lib import segmentation_lib
from lib import study_lib

from lib import schema


REPORT_JSON_SCHEMA_PATH = os.path.join(Path().absolute(), '../types/spine-report.schema.json')
REPORT_TEMPLATES_PATH = os.path.join(Path().absolute(), 'report_templates/dist/')
VIEWER_HTML_PATH = os.path.join(Path().absolute(), 'bin/viewer/')

REPORT_VERSIONS = {
    'HTML_VIEWER': '20210803',
    'PDF_SIMPLE': '20210803',
    'JSON': '20210803',
}


@orm.db_session
def generate_reports(study, report_types, classifications=None):
    """Generates the Reports to perform by default for each Study.

    Args:
        study: (schema.Study)
        report_types: list(str) eg. ['HTML_VIEWER']
        classifications: list(schema.Classification)

    Returns:
        (list(schema.Report))
    """
    # Re-fetch objects for this db_session.
    db_study = schema.Study.select(lambda s: s.id == study.id)[:]
    if not len(db_study):
        logging.error(
            'Could not find Study ID "{}" in database to generate new '
            'Report.'.format(
                study.id))
        return []
    db_study = db_study[0]

    if classifications is None:
        classifications = schema.Classification.select(lambda c: c.study == study)
    classification_ids = [c.id for c in classifications]
    db_classifications = schema.Classification.select(lambda c: c.id in classification_ids)[:]
    if len(db_classifications) != len(classifications):
        logging.error(
            'Asked to create report with "{}" Classifications but only found '
            '"{}" in database: expected: "{}", got: "{}"'.format(
                len(classifications),
                len(db_classifications),
                ','.join(classification_ids),
                ','.join([c.id for c in db_classifications])))
        return []

    reports = []
    for report_type in report_types:
        try:
            _ = schema.ReportType[report_type]
        except KeyError as e:
            logging.error('Unrecognized ReportType: %s', report_type)

        report = schema.Report(type=report_type)

        report.input_studies.add(db_study)
        for c in db_classifications:
            report.input_classifications.add(c)

        reports.append(report)

    return reports


class ReportMixin(object):
    """Member functions for the schema.Report object."""

    def process(self):
        if not len(self.input_studies):
            raise IndexError('No input_studies in Report.')

        # Load latest Segmentation for each type.
        segmentations_by_type = {}
        for c in self.input_classifications:
            for s in c.output_segmentations:
                if (s.type in segmentations_by_type and
                    s.creation_datetime <
                    segmentations_by_type[s.type].creation_datetime):
                    continue
                segmentations_by_type[s.type] = s

        if self.type == schema.ReportType.PDF_SIMPLE.name:
            self.version = REPORT_VERSIONS['PDF_SIMPLE']
            if len(self.input_studies) > 1:
                logging.warning(
                        'PDF_SIMPLE report uuid "{}": expected 1 input study, '
                        'got "{}". Using random study as input.'.format(
                            self.uuid, len(self.input_studies)))

            study = next(iter(self.input_studies))

            # Get PDF report and write bytes to database.
            report_writer = PDFReportWriter()
            report_writer.load_study(
                    study, segmentations_by_type.values())
            with tempfile.TemporaryDirectory() as tmp_dir:
                pdf_path = report_writer.write_simple_pdf(tmp_dir)
                with open(pdf_path, 'rb') as f:
                    self.report_bytes = f.read()

            # Set metadata
            self.num_narrow_slices = report_writer.report_vars['measurements']['canal_narrowing']['num_narrow_slices']
            self.surgery_recommended = report_writer.report_vars['measurements']['canal_narrowing']['surgery_recommended']

        elif self.type == schema.ReportType.HTML_VIEWER.name:
            self.version = REPORT_VERSIONS['HTML_VIEWER']
            # TODO(billy): Improve PDFReportWrite to make this code more DRY.
            if len(self.input_studies) > 1:
                logging.warning(
                        'HTML_VIEWER report uuid "{}": expected 1 input study, '
                        'got "{}". Using random study as input.'.format(
                            self.uuid, len(self.input_studies)))

            study = next(iter(self.input_studies))

            # Get PDF report and write bytes to database.
            report_writer = PDFReportWriter(
                    templates_path=VIEWER_HTML_PATH,
                    template_file='viewer.html')
            report_writer.load_study(
                    study, segmentations_by_type.values())
            with tempfile.TemporaryDirectory() as tmp_dir:
                html_path = report_writer.write_simple_html(tmp_dir)
                html_str = webpage2html.generate(html_path, keep_script=True, verbose=False)
                with open(html_path, 'rb') as f:
                    self.report_bytes = html_str.encode()
        elif self.type == schema.ReportType.JSON.name:
            self.version = REPORT_VERSIONS['JSON']

            study = next(iter(self.input_studies))

            report_writer = JSONReportWriter()
            report_writer.load_study(
                    study, segmentations_by_type.values())

            self.report_bytes = report_writer.get_bytes()
        else:
            raise ValueError('Unrecognized ReportType "{}".'.format(self.type))


# TODO(billy): Make report not depend on a path and rename.
class PDFReportWriter(object):
    """Write report HTML and PDF files from a Study."""

    # TODO(billy): Create standalone HTML files with embedded assets instead of
    # using directories.
    def __init__(self,
            templates_path=REPORT_TEMPLATES_PATH,
            template_file="report_simple.html",
            options=None):
        self.templates_path = templates_path
        self.template_file = template_file

        self.segmentations_by_type = {}

    @property
    def report_vars(self):
        if not hasattr(self, '_report_vars'):
            self._report_vars = {
                'report_date': datetime.today().strftime('%m/%d/%Y'),
            }
        return self._report_vars

    @property
    def pdfkit_options(self):
        if not hasattr(self, '_pdfkit_options'):
            self._pdfkit_options = {
                    'dpi': '400',
                    'encoding': 'UTF-8',
                    'margin-top': '0in',
                    'margin-right': '0.5in',
                    'margin-bottom': '0in',
                    'margin-left': '0.5in',
                    'orientation': 'Landscape',
                    'page-size': 'Letter',
                    'print-media-type': '',
            }
        return self._pdfkit_options

    def load_study(self, study, segmentations):
        """Import vars and assets required for rendering a report.

        Args:
            study: (schema.Study)
            segmentations: (list(schema.Segmentation))
        """
        self.report_vars['report_id'] = uuid.uuid4()
        self.report_vars['study'] = study

        for s in segmentations:
            self.segmentations_by_type[s.type] = s

        canal_segmentation = self.segmentations_by_type[
                schema.SegmentationType.CANAL.name].canal_segmentation
        disk_segmentation = self.segmentations_by_type[
                schema.SegmentationType.DISK.name].disk_segmentation
        foramen_segmentation = self.segmentations_by_type[
                schema.SegmentationType.FORAMEN.name]

        patient_age_years = (
                study.patient_age_years or constants_lib.AVERAGE_AGE_YEARS)
        patient_height_inches = (
            study.patient_height_inches or constants_lib.AVERAGE_HEIGHT_IN)

        # canal_locations_mm = disk_segmentation.get_disk_locations_mm()[:5]

        if canal_segmentation.segmentation.preprocessed_patient_series.metadata:
            canal_spacing = canal_segmentation.segmentation.preprocessed_patient_series.metadata[0x00280030].value
        else:
            canal_spacing = [1.0, 1.0, 1.0]

        all_canal_areas = canal_segmentation.get_all_canal_areas()

        canal_num_slices = canal_segmentation.series.image.GetDepth()
        canal_image_positions = [canal_segmentation.series.get_image_position(i) for i in range(canal_num_slices)]
        canal_slices = canal_segmentation.get_disc_levels()
        canal_areas = canal_segmentation.get_canal_areas_for_indicies(
                canal_slices,
                canal_spacing)
        canal_expected_areas = canal_segmentation.get_expected_areas(
                patient_age_years,
                patient_height_inches,
                study.patient_sex_enum)
        canal_percentage_of_nearest_slices = canal_segmentation.get_percentage_of_nearest_slices_for_indicies(canal_slices, canal_spacing)

        # canal_slices = [canal_segmentation.get_nearest_index_from_mm(l) for l in canal_locations_mm]
        canal_seg_images = [
                'canal_segmentation/postprocessed_segmentation_series/'
                'image-%03d.png' % (i) for i in canal_slices]
        canal_images = [
                'canal_segmentation/preprocessed_patient_series/'
                'image-%03d.png' % (i) for i in canal_slices]

        canal_height = canal_segmentation.segmentation.postprocessed_segmentation_series.image.GetHeight()
        canal_width = canal_segmentation.segmentation.postprocessed_segmentation_series.image.GetWidth()



        cutline_measurement = clinical_lib.CutlineMeasurement(
                foramen_segmentation.postprocessed_segmentation_series,
                canal_segmentation.segmentation.postprocessed_segmentation_series)
        geisinger_measurement = clinical_lib.GeisingerMeasurement(canal_segmentation)

        # Adjust geisinger rendering for non-256px canal images.
        geisinger_measurements = geisinger_measurement.get_measurements()
        for i, gcanal_height in enumerate(geisinger_measurements['canal_heights']):
            gcanal_height['origin'] = (
                gcanal_height['origin'][0] * (256.0 / canal_height),
                gcanal_height['origin'][1] * (256.0 / canal_width))
            gcanal_height['px_height'] *= 256.0 / canal_height
        for i, gcanal_width in enumerate(geisinger_measurements['canal_widths']):
            gcanal_width['origin'] = (
                gcanal_width['origin'][0] * (256.0 / canal_height),
                gcanal_width['origin'][1] * (256.0 / canal_width))
            gcanal_width['px_width'] *= 256.0 / canal_width


        narrowing_measurement = clinical_lib.CanalNarrowingMeasurement(canal_segmentation)


        self.report_vars['measurements'] = {
                cutline_measurement.name(): cutline_measurement.get_measurements(),
                geisinger_measurement.name(): geisinger_measurements,
                narrowing_measurement.name(): narrowing_measurement.get_measurements(),
        }
        self.report_vars['canal_segmentation'] = {
                'canal_height': canal_height,
                'canal_width': canal_width,
                'canal_slices': canal_slices[:5],
                'canal_slice_images': canal_images[:5],
                'canal_seg_images': canal_seg_images[:5],
                'all_canal_areas': all_canal_areas,
                'image_positions': canal_image_positions,
                'canal_areas': canal_areas[:5],
                'canal_expected_areas': canal_expected_areas,
                'canal_percentage_of_nearest_slices': canal_percentage_of_nearest_slices,
                'orientation': canal_segmentation.series.get_render_orientation()
        }
        self.report_vars['disk_segmentation'] = {
                'num_slices': disk_segmentation.series.image.GetDepth(),
                'orientation': disk_segmentation.series.get_render_orientation()
        }
        self.report_vars['foramen_segmentation'] = {
                'num_slices': foramen_segmentation.preprocessed_patient_series.image.GetDepth()
        }


    def write_simple_html(self, path, overwrite=True):
        """Writes a report_simple.html file to the given path.

        Also writes assets (eg. styles and images)
        """
        # Copy required assets.
        if os.path.exists(path):
            if overwrite:
                shutil.rmtree(path)
            else:
                raise FileExistsError('File Exists: "%s"' % path)

        copy_tree(self.templates_path, path)

        canal_segmentation = self.segmentations_by_type[
                schema.SegmentationType.CANAL.name]
        canal_segmentation.to_dir(
                os.path.join(path, 'canal_segmentation'))
        if self.template_file == 'viewer.html':
            disk_segmentation = self.segmentations_by_type[
                    schema.SegmentationType.DISK.name]
            disk_segmentation.to_dir(
                    os.path.join(path, 'disk_segmentation'))
            foramen_segmentation = self.segmentations_by_type[
                    schema.SegmentationType.FORAMEN.name]
            foramen_segmentation.to_dir(
                    os.path.join(path, 'foramen_segmentation'))

        jinja_env = Environment(extensions=['jinja2.ext.do'])
        jinja_env.filters.update({'to_json': json.dumps})
        template_path = os.path.join(path, self.template_file)
        with open(template_path, 'r') as f:
            template = jinja_env.from_string(f.read())

        with open(template_path, 'w') as f:
            report_html = template.render(**self.report_vars)
            f.write(report_html)

        return template_path

    # TODO(billy): Make this take an HTML file and write a PDF file.
    def write_simple_pdf(self, path):
        """Writes a report_simple.pdf file to the given path.

        Expected to be called after write_html().

        Returns:
            (str) Path to report_simple.pdf.
        """
        self.write_simple_html(path, overwrite=True)

        template_path = os.path.join(path, self.template_file)

        if not os.path.exists(template_path):
            logging.error('No {} template found in "{}"'.format(
                self.template_file, path))

        pdf_filename = self.template_file.replace('html', 'pdf')
        pdf_path = os.path.join(path, pdf_filename)

        pdfkit.from_url(template_path, pdf_path, options=self.pdfkit_options)
        return pdf_path

class JSONReportWriter(object):

    def __init__(self):
        self.data = {}

        self.schema = {}
        with open(REPORT_JSON_SCHEMA_PATH, 'r') as f:
            self.schema = json.load(f)

    def load_study(self, study, segmentations):
        # We reuse the load_study logic from PDFReportWriter here.
        # TODO(billy): Clean up load_study in PDFWriter and use JSON-specific
        # logic here.
        pdf_writer = PDFReportWriter()
        pdf_writer.load_study(study, segmentations)
        self.data = pdf_writer.report_vars
        self.data['errors'] = []
        self.data.pop('report_id', None)
        self.data.pop('study', None)

        try:
            jsonschema.validate(
                    instance=self.data,
                    schema=self.schema)
        except jsonschema.ValidationError as e:
            # TODO(billy): Consider encapsulating json in python object to make
            # operations cleaner.
            self.data['errors'].append(str(e).partition('\n')[0])


    def get_bytes(self):
        json_str = json.dumps(self.data)
        return json_str.encode('utf-8')

