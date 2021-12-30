#!/user/bin/env python
"""Tool for exporting studies from databases into a directory."""

import argparse
import logging
import os
import sys
import threading

from PIL import Image
from pony import orm
import SimpleITK

from lib import database_lib
from lib import img_lib

from lib import schema


def export_segmentation(segmentation, study_dir):
    output_dir = os.path.join(study_dir, 'segmentations', segmentation.type)
    seg_num = 0
    while os.path.isdir(output_dir):
        output_dir = os.path.join(study_dir, 'segmentations', segmentation.type + seg_num)
        seg_num += 1

    if segmentation.preprocessed_patient_series:
        preprocessed_path = os.path.join(output_dir, 'preprocessed_patient_series_png')
        if not os.path.exists(preprocessed_path):
            os.makedirs(preprocessed_path, exist_ok=True)
        segmentation.preprocessed_patient_series.to_dir(preprocessed_path, file_type='png')

        preprocessed_path = os.path.join(output_dir, 'preprocessed_patient_series')
        if not os.path.exists(preprocessed_path):
            os.makedirs(preprocessed_path, exist_ok=True)

        writer = SimpleITK.ImageFileWriter()
        # NOTE: We don't write DCM files here because GDCM doesn't support it.
        # We should either export the original image or convert pixel values to
        # integers.
        writer.SetImageIO("MetaImageIO")
        writer.SetFileName(os.path.join(preprocessed_path, 'image.mha'))
        writer.Execute(segmentation.preprocessed_patient_series.image)
        writer.SetImageIO("NiftiImageIO")
        writer.SetFileName(os.path.join(preprocessed_path, 'image.nii'))
        writer.Execute(segmentation.preprocessed_patient_series.image)



    rgb_pixel = (100, 100, 100)
    if segmentation.type == 'CANAL':
        rgb_pixel = (255, 0, 0)
    elif segmentation.type == 'DISK':
        rgb_pixel = (0, 255, 0)
    elif segmentation.type == 'FORAMEN':
        rgb_pixel = (0, 0, 255)

    for image, dirname in [
            (segmentation.raw_segmentation_series.image, 'raw_segmentation_series'),
            (segmentation.postprocessed_segmentation_series.image, 'postprocessed_segmentation_series')]:

        png_path = os.path.join(output_dir, dirname + '_png')
        if not os.path.exists(png_path):
            os.makedirs(png_path, exist_ok=True)
        img_lib.pretty_write_segmentation_img(image, png_path)

        raw_path = os.path.join(output_dir, dirname)
        if not os.path.exists(raw_path):
            os.makedirs(raw_path, exist_ok=True)
        castFilter = SimpleITK.CastImageFilter()
        castFilter.SetOutputPixelType(SimpleITK.sitkUInt16)
        image_cast = castFilter.Execute(image)
        writer = SimpleITK.ImageFileWriter()
        writer.SetImageIO("GDCMImageIO")
        writer.SetFileName(os.path.join(raw_path, 'image_bw.dcm'))
        writer.Execute(image_cast)

        raw_rgb_image = img_lib.convert_mask_to_rgb(image, rgb_pixel)
        writer.SetImageIO("MetaImageIO")
        writer.SetFileName(os.path.join(raw_path, 'image_rgb.mha'))
        writer.Execute(raw_rgb_image)
        writer.SetImageIO("NiftiImageIO")
        writer.SetFileName(os.path.join(raw_path, 'image_rgb.nii'))
        writer.Execute(raw_rgb_image)
        writer.SetImageIO("GDCMImageIO")
        writer.SetFileName(os.path.join(raw_path, 'image_rgb.dcm'))
        writer.Execute(raw_rgb_image)

def export_viewer(report, export_dir, filename='viewer.html'):
    with open(os.path.join(export_dir, filename), 'wb') as f:
        f.write(report.report_bytes)

def export_study(study, study_dir):
    logging.info('Exporting study "{}".'.format(study.name))

    # Export segmentations
    for segmentation in study.segmentations:
        export_segmentation(segmentation, study_dir)

    # Export HTML debug viewers.
    has_viewer = False
    for report in study.reports:
        if report.type == 'HTML_VIEWER' and report.report_bytes:
            export_viewer(report, study_dir)
            has_viewer = True
    if not has_viewer:
        logging.warning('No viewer found for study "{}":'.format(study.name))

def main():
    parser = argparse.ArgumentParser(
            description='Tool for exporting studies as files.')

    parser.add_argument(
            '--sqlite_file',
            required=True,
            help='(required) SQLite file containing an existing Spine AI '
                 'database.')
    parser.add_argument(
            '--output_dir',
            required=True,
            help='(optional) Output directory.')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info('Initializing and connecting to the SpineAI database...')
    sqlite_file = os.path.abspath(args.sqlite_file)
    db = database_lib.SpineAIDatabase(
            db_location=sqlite_file,
            db_debug=False)
    db.connect(create_tables=True)

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    if not os.path.isdir(args.output_dir):
        logging.error(
                'Could not create missing directory {}'.format(output_dir))
        sys.exit(1)

    with orm.db_session:
        for study in schema.Study.select():
            study_dir = os.path.join(args.output_dir, study.name)
            if os.path.isdir(study_dir):
                logging.error(
                        'Directory {} already exists. Most likely a duplicate '
                        'study. Ignoring duplicate...'.format(study_dir))
                continue

            os.mkdir(study_dir)
            export_study(study, study_dir)


if __name__ == '__main__':
    main()
