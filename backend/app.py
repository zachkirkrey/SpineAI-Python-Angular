#!/usr/bin/env python

import argparse
import logging
import os
from pathlib import Path
import sys

from config2.config import config
# NOTE(billy): This hack is here because the config2 library adds a None object
# to sys.path in our Docker environment. Not sure why this happens.
# TODO(billy): Use a more production ready python configuration system.
sys.path = [i for i in sys.path if i]

from pony import orm

from lib import database_lib
from runtime import backend_api
from runtime import database_listener
from runtime import study_reader
from yoyo import read_migrations
from yoyo import get_backend


class Tee(object):
    """Write logs to stdout and file, like the tee comand."""
    def __init__(self, name, mode="w"):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
    def flush(self):
        self.file.flush()

# This uses yoyo-migrations to perform database additions to entities missing new columns
# (new entities and relations are automatically handled by pony)
# See https://ollycope.com/software/yoyo/6.1.0/ for documentation about writing and working with migrations
def migrate(location):
    logging.info('Migrating database at: "sqlite:///%s"', location)
    backend = get_backend('sqlite:///' + location)
    logging.info('Migration path "%s"', os.path.abspath('lib/migrations'))
    migrations = read_migrations('lib/migrations')
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

def main():
    # Get command line configuration
    parser = argparse.ArgumentParser(
            description='\x1b[34mSpineAI main app\x1b[0m: Classify and '
                        'generate reports for MRI studies.\n'.format(
                            scriptname=sys.argv[0],
                            path=Path().absolute()),
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
            '--db_location',
            help='(optional) Override the config-provided location for the '
                 'database.')
    parser.add_argument(
            '--input_dir',
            help='(optional) Override the config-provided location for the '
                 'input directory.')
    parser.add_argument('--daemon', action='store_true')
    parser.add_argument('--nodaemon', action='store_true')

    args = parser.parse_args()

    # Override file configuration if command line values provided.
    logging.info('Using config environment: "%s"', config.get_env())
    if args.db_location:
        logging.info(
                'Command line override: db_location: "%s"',
                args.db_location)
        config.spineai.runtime.storage.location = args.db_location
    if args.input_dir:
        logging.info(
                'Command line override: input_dir: "%s"',
                args.input_dir)
        config.spineai.runtime.input.location = args.input_dir
    if args.daemon and args.nodaemon:
        raise ValueError('--daemon and --nodaemon are mutually exclusive.')
    if args.daemon:
        logging.info('Command line override: daemon: True')
        config.spineai.runtime.daemon = True
    if args.nodaemon:
        logging.info('Command line override: daemon: False')
        config.spineai.runtime.daemon = False


    # Log to file and to termnal.
    logging.basicConfig(
            level=config.spineai.logging.loglevel,
            handlers=[
                logging.FileHandler(config.spineai.logging.logfile),
                logging.StreamHandler()
            ],
            format='%(levelname)s:%(name)s:\x1b[34m%(message)s\x1b[0m')
    if config.spineai.logging.stdout_logfile:
        tee_logger = Tee(config.spineai.logging.stdout_logfile)


    # Set up the SpineAI database.
    dbconfig = config.spineai.runtime.storage
    dbconfig.location = os.path.abspath(dbconfig.location)
    logging.info('Initializing and connecting to %s', dbconfig.location)
    db = None
    if dbconfig.engine == 'sqlite3':
        migrate(dbconfig.location)
        db = database_lib.SpineAIDatabase(
                db_location=dbconfig.location,
                db_debug=dbconfig.debug)
        db.connect(create_tables=True)
    else:
        raise NotImplementedError(
                'Invalid database engine: "{}"'.format(dbconfig.engine))

    # Ingest input directories.
    inputconfig = config.spineai.runtime.input
    if inputconfig.location:
        inputconfig.location = os.path.abspath(inputconfig.location)
        logging.info('Ingesting studies from directories in {}...'.format(
            inputconfig.location))
        reader = study_reader.StudyReader(
                do_classify = config.spineai.classification.settings.do_classify,
                report_types = config.spineai.report.types)
        reader.ingest_studies(inputconfig.location)

    # Start DICOM proxy server.
    api_server = backend_api.APIServer('', config.spineai.http_server.port)
    api_server.run_in_thread()

    # Listen on and process queued studies from SQL.
    logging.info('Starting SpineAI and listening on database events.')
    listener = database_listener.DatabaseListener(
            debug=config.spineai.runtime.debug,
            daemon=config.spineai.runtime.daemon)
    listener.run()

if __name__ == '__main__':
    main()
