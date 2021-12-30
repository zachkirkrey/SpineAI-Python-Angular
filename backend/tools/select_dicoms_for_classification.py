#!/user/bin/env python
"""Tool for selecting series from a DICOM study for classification."""

import argparse
import logging
import os

from pony import orm
import SimpleITK

from lib import schema
from lib import classifier_lib
from lib import database_lib
from runtime import study_reader



def main():
    parser = argparse.ArgumentParser(
            description='Tool for selecting series from studies.')

    parser.add_argument(
            '--db_location',
            required=True,
            help='(required) SQLite file for app state.')
    parser.add_argument(
            '--input_dir',
            required=True,
            help='(required) Directory containing DICOM studies.')
    parser.add_argument(
            '--output_dir',
            required=True,
            help='(required) Directory to place output series.')

    args = parser.parse_args()

    db = database_lib.SpineAIDatabase(
            db_location=args.db_location,
            db_debug=False)
    db.connect(create_tables=True)

    reader = study_reader.StudyReader(do_classify=False)
    reader.ingest_studies(args.input_dir)

    os.makedirs(args.output_dir, exist_ok=True)

    with orm.db_session:
        studies = orm.select(s for s in schema.Study)

        for study in studies:
            series = study.patient_series
            if len(series) < 1:
                logging.error('Study has 0 series. Skipping...')
                continue


            axial_series = classifier_lib.DefaultCanalClassifier.sorted_by_fit(series)[0]

            sagittal_series = classifier_lib.DefaultForamenClassifier.sorted_by_fit(series)[0]

            study_dirname = os.path.join(args.output_dir, study.name)
            os.mkdir(study_dirname)

            axial_dirname = os.path.join(study_dirname, 'axial')
            os.mkdir(axial_dirname)
            writer = SimpleITK.ImageFileWriter()
            writer.SetImageIO('GDCMImageIO')
            writer.SetFileName(os.path.join(axial_dirname, 'axial.dcm'))
            cast_filter = SimpleITK.CastImageFilter()
            cast_filter.SetOutputPixelType(SimpleITK.sitkUInt16)
            axial_image = cast_filter.Execute(axial_series.image)
            writer.Execute(axial_image)

            sagittal_dirname = os.path.join(study_dirname, 'sagittal')
            os.mkdir(sagittal_dirname)
            writer.SetFileName(os.path.join(sagittal_dirname, 'sagittal.dcm'))
            sagittal_image = cast_filter.Execute(sagittal_series.image)
            writer.Execute(sagittal_image)






if __name__ == '__main__':
    main()
