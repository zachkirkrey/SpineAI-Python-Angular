"""Library for managing the SpineAI database."""

from enum import IntEnum, auto
import logging

from pony import orm

from lib import schema

from runtime import study_reader


class DatabaseType(IntEnum):
    SQLITE = auto()


class SpineAIDatabase(object):

    def __init__(
            self,
            db_location,
            db_type=DatabaseType.SQLITE,
            db_debug=False):
        """This class manages a SpineAI database.

        Args:
            db_type: (DatabaseType)
            db_location:
                DatabaseType.SQLITE: Filename for the database.
        """
        self.db_type = db_type
        self.db_location = db_location
        self.ponydb = schema.db

        orm.set_sql_debug(db_debug)

    def connect(self, create_tables=False):
        if self.db_type == DatabaseType.SQLITE:
            self.ponydb.bind(
                    provider='sqlite', filename=self.db_location, create_db=True)
            self.ponydb.generate_mapping(create_tables=create_tables)
        else:
            raise ValueError('Invalid DatabaseType "{}"'.format(self.db_type))
