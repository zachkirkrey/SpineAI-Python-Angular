#!ven/bin/python
"""Simple app to ingest a DICOM Study into a SQLite database."""

import argparse
import logging
import os

from lib import database_lib
from runtime import study_reader

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '--sqlite_file',
        default='database.db',
        help='(required) SQLite file containing an existing Spine AI '
             'database.')
    parser.add_argument(
            '--input_dir',
            required=True,
            help='(required) Directory containing DICOM files to ingest.')

    parser.add_argument(
            '--sqlite_debug',
            action='store_true',
            help='(optional) If set, print sql queries.')

    args = parser.parse_args()

    logging.basicConfig(
            level=logging.INFO,
            handlers=[
                # logging.FileHandler(),
                logging.StreamHandler()
            ],
            format='%(levelname)s:%(name)s:\x1b[34m%(message)s\x1b[0m')

    sqlite_file = os.path.abspath(args.sqlite_file)
    db = database_lib.SpineAIDatabase(
            db_location=sqlite_file,
            db_debug=args.sqlite_debug)
    db.connect(create_tables=True)

    reader = study_reader.StudyReader()
    reader.ingest_study(
            args.input_dir,
            create_classification=True,
            create_report=True)

if __name__ == '__main__':
    main()
