#!venv/bin/python
"""Simple app to inspect data in the SpineAI database."""

import argparse
import os
from pathlib import Path
import sys

from pony import orm
import SimpleITK

from lib import database_lib
from lib import schema

def main():
    parser = argparse.ArgumentParser(
            description='\x1b[34mSpineAI main app\x1b[0m: Classify and '
                        'generate reports for MRI studies.\n'.format(
                            scriptname=sys.argv[0],
                            path=Path().absolute()),
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
            '--sqlite_file',
            default='database.db',
            help='(required) SQLite file containing an existing Spine AI '
                 'database, or a new one to be created.')
    parser.add_argument(
            '--sqlite_debug',
            action='store_true',
            help='(optional) If set, print sql queries.')

    args = parser.parse_args()

    # Set up the SpineAI database.
    sqlite_file = os.path.abspath(args.sqlite_file)
    db = database_lib.SpineAIDatabase(
            db_location=sqlite_file,
            db_debug=args.sqlite_debug)
    db.connect(create_tables=False)


    with orm.db_session:
        study = schema.Study[1]
        canal_segmentation = schema.Segmentation.select(
                lambda seg: (seg.type == 'CANAL' and seg.study == study))[:][0]

        SimpleITK.Show(canal_segmentation.preprocessed_patient_series.image)

if __name__ == '__main__':
    main()
