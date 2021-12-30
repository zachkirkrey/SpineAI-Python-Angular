import argparse
import logging
import os
import re

import pydicom

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dicom_file')
    parser.add_argument('--max_dirs', default=100)
    # parser.add_argument('--out_file_name', default='metadata.txt')
    args = parser.parse_args()

    dicom_path = args.dicom_file
    max_dirs = args.max_dirs
    # out_file_name = args.out_file_name

    walk = os.walk(dicom_path)
    num_dirs = 0
    for w in walk:
        num_dirs += 1
        if num_dirs > max_dirs:
            break

        # We process the first .dcm file in each subdirectory.
        (dirpath, unused_dirnames, filenames) = w
        index = 0
        for filename in filenames:
            # if re.match('.+dcm$', filename):
            full_path = os.path.join(dirpath, filename)
            try:
                metadata = pydicom.dcmread(full_path)
            except pydicom.errors.InvalidDicomError as e:
                logging.error('Could not read DICOM metadata from {}.'.format(full_path))
                continue

            # Write a metadata.txt file.
            metadata_path = os.path.join(dirpath, 'metadata_' + str(index) + '.txt')
            index += 1
            # print(metadata_path)
            with open(metadata_path, 'w') as f:
                # print(str(metadata))
                f.write(str(metadata))


if __name__ == '__main__':
    main()
