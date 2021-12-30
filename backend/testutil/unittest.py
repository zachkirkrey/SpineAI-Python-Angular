"""Ponos specific unittests with extra features/parameters."""

import logging
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from lib import database_lib

from lib.schema import db as ponydb


PROJECT_PATH = Path().absolute()

TEST_DATABASE = os.path.join(PROJECT_PATH, 'testdata/database/database.db')

DBFILE = None

class TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use $LOG_LEVEL or INFO log level by default.
        log_level = os.environ.get('LOG_LEVEL', logging.INFO)
        logging.basicConfig(level=log_level)

        global DBFILE
        if DBFILE is None:
            DBFILE = tempfile.NamedTemporaryFile()
            with open(TEST_DATABASE, 'rb') as f:
                DBFILE.write(f.read())

        if not ponydb.provider:
            db = database_lib.SpineAIDatabase(DBFILE.name)
            db.connect()


def main():
    unittest.main()
