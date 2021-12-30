"""Schema for QA PostgreSQL instance."""
from enum import Enum
from datetime import datetime

from pony.orm import *

db = Database()

class StudyType(Enum):
    DICOM_ZIP = 'DICOM_ZIP'

class Study(db.Entity):
    _table_ = ('qa', 'study')
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    creation_datetime = Required(datetime, default=datetime.now)

    hash_type = Required(str)
    hash_value = Required(bytes)

    study_type = Required(str)
    study_source = Required(str)
    study_data = Required(bytes)



