#!/user/bin/env python
"""Tool for calculating the canal areas of segmented images."""

import argparse
import csv
import glob
import logging
import os
import sys

import SimpleITK

from lib import img_lib

IMAGE_DIR='/opt/spineai/files/UCLA_Validation_500/The500/mask/'
OUTPUT_CSV=os.path.join(os.getcwd(), 'output.csv')

def main():
    parser = argparse.ArgumentParser(description='')

    args = parser.parse_args()

    # This tool was originally built for the hand segmented images in the UCLA_Validation_500 set, as
    # described in https://docs.google.com/spreadsheets/d/1K2_17TCEqDgiO2siibRegntfB_HGak7u3Hw834c1Hw0/edit#gid=0

    outputs = {}

    reader = SimpleITK.ImageSeriesReader()
    reader.SetOutputPixelType(SimpleITK.sitkFloat32)

    filepaths = list(glob.glob(os.path.join(IMAGE_DIR, '*.nii.gz')))
    filepaths.sort()
    for filepath in filepaths:
        output = {
                'warnings': [],
                'areas': [],
        }
        reader.SetFileNames([filepath])
        try:
            image = reader.Execute()
        except RuntimeError as e:
            logging.error(
                    'RuntimeError ({}) while reading series. '.format(str(e)))
            sys.exit(1)

        image_array = SimpleITK.GetArrayFromImage(image)
        if len(image_array) == 1:
            image_array = image_array[0]
        else:
            logging.error(
                    'Unexpected NIFTI shape: %s', image_array.shape)
            sys.exit(1)

        for i, s in enumerate(image_array):
            areas = list(img_lib.get_all_areas_array(s))
            if len(areas) > 1:
                output['warnings'].append(
                        '{} areas for slice {}. Reporting largest area.'.format(len(areas), i))

            area_value = 0
            for area in areas:
                if area['size'] > area_value:
                    area_value = area['size']
            output['areas'].append(area_value)

        filename = os.path.basename(filepath)
        outputs[filename] = output

    # Write CSV
    headers = [
            'Filename',
            'Warnings',
            'Canal Areas']
    with open(OUTPUT_CSV, 'w', newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(headers)
        for filename in outputs:
            output = outputs[filename]
            row = [
                    filename,
                    output['warnings']]
            row.extend(output['areas'])
            csvwriter.writerow(row)



if __name__ == '__main__':
    main()
