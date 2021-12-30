#!/usr/bin/env python
"""Get studies from PostgreSQL."""

import argparse
import logging
import os
import pwd
import tempfile
import zipfile

from pony.orm import *

from lib import schema


@db_session
def unzip_study(study_id, path):
    study = select(s for s in schema.Study
                   if s.id == study_id)
    study = list(study)
    if not len(study):
        raise ReferenceError('Study(id={}) not found.'.format(study_id))

    study = study[0]
    zip_path = os.path.join(path, study.name)
    if os.path.isdir(zip_path):
        logging.error('Error: Directory {} already exists. Skipping...'.format(
            zip_path))
        return
    os.mkdir(zip_path)

    logging.info('Unzipping...')
    with tempfile.TemporaryFile(mode='w+b') as f:
        f.write(study.study_data)
        with zipfile.ZipFile(f, 'r', zipfile.ZIP_LZMA) as zipf:
            zipf.extractall(zip_path)

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
            '--num_studies',
            required=True,
            type=int,
            help='Number of studies to retrieve.')
    parser.add_argument(
            '--output_dir',
            required=True,
            help='Directory to write studies.')

    args = parser.parse_args()

    schema.db.bind(
            provider='postgres',
            host=args.db_host,
            user=args.db_user,
            password=os.environ['POSTGRES_PASSWORD'],
            database=args.db_database)
    schema.db.generate_mapping(create_tables=False)

    with db_session:
        s = select(
                (s.id, s.name, s.study_source, s.hash_value)
                for s in schema.Study).order_by(
                lambda sid, name, source, hash_value: source + name)
        s = list(s)

        studies = {}
        for sid, name, source, hash_value in s:
            if source not in studies:
                studies[source] = []

            studies[source].append((name, hash_value))

        for study_source in studies:
            logging.info('{}: {} Studies.'.format(
                study_source, len(studies[study_source])))
        logging.info('Total studies: {}'.format(len(s)))

    num_studies = 0
    for sid, name, source, hash_value in s:
        if num_studies + 1 > args.num_studies:
            break

        logging.info('Fetching Study(id={}, name={}, study_source={}'.format(
           sid, name, source))
        unzip_study(sid, args.output_dir)

        num_studies += 1



if __name__ == '__main__':
    main()
