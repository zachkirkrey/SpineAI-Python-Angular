#!/usr/bin/env python
"""Upload studies to PostgreSQL."""

import argparse
import logging
import os
import pwd
import sys
import struct
import tempfile
import zipfile
import zlib

from pony.orm import *

from lib import schema

def get_zipped_bytes(path):
    """Zip the given directory and return as bytes."""
    if not os.path.isdir(path):
        raise TypeError('{} is not a valid directory.'.format(path))

    logging.info('zipping {}...'.format(path))
    with tempfile.TemporaryFile(mode='w+b') as f:
        with zipfile.ZipFile(f, 'w', zipfile.ZIP_LZMA) as zipf:
            for root, dirs, files in os.walk(path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(file_path, path)
                    zipf.write(file_path, rel_path)

        f.seek(0)
        bytes = f.read()

    return bytes

def get_hash(b):
    """Get hash of given bytes."""
    return zlib.crc32(b)

@db_session
def write_study(name, source, path, study=None):
    """Write Study to database. If study != None, overwrite existing study."""
    zipped_bytes = get_zipped_bytes(path)
    print('Zipped size: {}MB.'.format(
        len(zipped_bytes) / 1000000))
    zipped_hash = get_hash(zipped_bytes).to_bytes(4, 'big')

    if study:
        if study.hash_value == zipped_hash:
            logging.info('Hash unchanged. Skipping...')
        else:
            logging.info('Overwriting {} to database...'.format(name))
            study.hash_value = zipped_hash
            study.study_data = zipped_bytes
    else:
        logging.info('Writing {} to database...'.format(name))
        study = schema.Study(
                name=name,
                hash_type='CRC32',
                hash_value=zipped_hash,
                study_type='DICOM_ZIP',
                study_source=source,
                study_data=zipped_bytes)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '--db_host',
            default='',
            help='PostgreSQL host.')
    parser.add_argument(
            '--db_user',
            default=pwd.getpwuid(os.getuid()).pw_name,
            help='PostgreSQL user.')
    parser.add_argument(
            '--db_database',
            help='PostgreSQL database.')

    parser.add_argument(
            '--studies_dir',
            required=True,
            help='(required) Directory containing studies to upload.')
    parser.add_argument(
            '--study_source',
            required=True,
            help='(required) String to use as study_source value for rows in '
                 'PostgreSQL. (eg. "UCLA_245")')

    args = parser.parse_args()

    # Connect to database.
    schema.db.bind(
            provider='postgres',
            host=args.db_host,
            user=args.db_user,
            password=os.environ['SQITCH_PASSWORD'],
            database=args.db_database)
    schema.db.generate_mapping(create_tables=False)

    (_, dirnames, _) = next(os.walk(args.studies_dir))
    dirnames.sort()
    logging.info('Directories: {}'.format(', '.join(dirnames)))
    logging.info('Found {} directories.'.format(len(dirnames)))
    c = input('Continue? (Y/n) ').lower()

    if c == '' or c == 'y':
        always_overwrite = False
        num_uploaded = 0

        n = input('# of studies to upload: (Press ENTER to upload all) ')
        n = int(n) if n else sys.maxsize

        for dirname in dirnames:
            if num_uploaded + 1 > n:
                break

            logging.info('Uploading study {}.'.format(dirname))
            full_path = os.path.join(args.studies_dir, dirname)

            # Find existing studies of same name and source.
            with db_session:
                s = select(s for s in schema.Study
                           if (s.study_source == args.study_source and
                               s.name == dirname))
                s = list(s)

            if len(s):
                existing_study = s[0]
                logging.warning(
                        'Study(study_name="{}", study_source="{}") already '
                        'exists in database.'.format(
                            existing_study.name, existing_study.study_source))

                if not always_overwrite:
                    overwrite = input('Overwrite? [Y/n/all] ').lower()
                    if overwrite == 'all':
                        always_overwrite = True

                if always_overwrite or overwrite == '' or overwrite == 'y':
                    write_study(dirname, args.study_source, full_path, existing_study)
            else:
                write_study(dirname, args.study_source, full_path)


            num_uploaded += 1

if __name__ == '__main__':
    main()
