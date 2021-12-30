"""Library for ingesting DICOM studies from disk into SpineAI."""

import glob
import logging
import os
import shutil

from config2.config import config
from pony import orm

from lib import classifier_lib
from lib import report_lib
from lib import schema
from lib import series_lib
from lib import study_lib
from lib import util_lib


class StudyReader(object):

    def __init__(self, debug=False, do_classify=True, report_types=None):
        if debug:
            orm.set_sql_debug(debug)

        self.do_classify = do_classify
        self.report_types = []
        if report_types:
            self.report_types = report_types

    def ingest_studies(self, input_dir):
        logging.info('Ingesting studies from "{}"'.format(input_dir))
        if not os.path.isdir(input_dir):
            raise ValueError(
                    'input_dir "{}" is not a valid directory.'.format(
                        input_dir))

        dirnames = next(os.walk(input_dir))[1]
        if not len(dirnames):
            logging.error(
                    'No subdirectories found in "{}". Did you place each study '
                    'in its own directory?'. format(input_dir))

        for dirname in dirnames:
            study_input_dir = os.path.join(input_dir, dirname)
            study = self.ingest_study(study_input_dir)

    @orm.db_session
    def ingest_study(self, input_dir, name=None):
        """Create a Study object from the files in the given directory.

        Args:
            input_dir: (str)
            name: (str)

        Returns:
            (schema.Study)
        """
        logging.info('Ingesting study from "{}"'.format(input_dir))
        try:
            study = self.read_study(input_dir, name)
        except ValueError as e:
            logging.error(e)
            logging.error('Skipping Study ingestion.')
            return None

        existing_study = orm.select(
                s for s in schema.Study
                if s.study_instance_uid == study.study_instance_uid)[:]
        existing_study_with_checksum = orm.select(
                s for s in schema.Study
                if (s.study_instance_uid == study.study_instance_uid and
                    s.file_dir_checksum == study.file_dir_checksum))[:]
        # NOTE(billy): There will always be at least one study with this UID
        # (the current, uncomitted study).
        if len(existing_study) > 1:
            if len(existing_study_with_checksum) > 1:
                logging.info(
                        'While processing "{}": An existing study with '
                        'identical UID "{}" and file checksum was found. '
                        'Skipping ingestion...'.format(
                            input_dir, study.study_instance_uid))
                orm.rollback()
                return

            logging.info(
                    'While processing "{}": An existing study with identical UID '
                    '"{}" but different file checksum was found. Creating new '
                    'entry...'.format(
                            input_dir, study.study_instance_uid))

        if self.do_classify:
            classifications = classifier_lib.generate_default_classifications(study)

            reports = report_lib.generate_reports(study, self.report_types)

        return study

    def read_study(self, input_dir, name=None):
        """Create a Study object from the given directory.

        Args:
            input_dir: (string) Directory tree containing DICOM files to read.
            name: (string) Optional name to attach to Study.

        Returns:
            (schema.Study)
        """
        # Extract input_dir/file.zip to input_dir/file_uncompressed/*,
        # unless output dir already exists.
        zip_paths = glob.glob(os.path.join(input_dir, '*.zip'))
        if zip_paths:
            for zip_path in zip_paths:
                zip_file_name = os.path.splitext(os.path.basename(zip_path))[0]
                zip_output_dir = os.path.join(
                        input_dir, zip_file_name + '_uncompressed')
                if os.path.exists(zip_output_dir):
                    logging.info('{0} already exists, skipping {1}'.format(
                        zip_output_dir, zip_path))
                else:
                    util_lib.unzip_to_dir(zip_path, zip_output_dir)

        logging.info('Creating Study from %s' % (input_dir))
        return study_lib.CreateStudy(input_dir, name)
