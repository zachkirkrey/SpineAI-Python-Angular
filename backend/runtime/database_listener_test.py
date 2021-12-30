"""Unit tests for database_listener.py"""

from testutil import unittest

import base64
import os
import tempfile
import time
import zipfile

from pony import orm

from runtime import database_listener

from lib import schema


DICOM_FILES = "/opt/spineai/spineai/backend/testdata/dicom_ucla_BAABQXXR"


class IngestionListenerTeset(unittest.TestCase):
    @orm.db_session
    def test_file_bytes_ingestion(self):
        with tempfile.NamedTemporaryFile('w+b') as f:
            with zipfile.ZipFile(f, 'w') as zipf:
                for dir_name, _, files in os.walk(DICOM_FILES):
                    for filename in files:
                        path = os.path.join(dir_name, filename)
                        zipf.write(path)

            f.seek(0)
            ingestion = schema.Ingestion(
                    type=schema.IngestionType.FILE_BYTES.name,
                    file_archive_bytes=base64.b64encode(f.read()))


        old_reports = orm.count(r for r in schema.Report)

        listener = database_listener.IngestionListener(debug=True)
        listener.run()

        self.assertEqual(ingestion.state, schema.EventState.PROCESSED.name)

        new_reports = orm.count(r for r in schema.Report)
        self.assertGreater(
                new_reports, old_reports,
                "No new Reports created on Ingestion.")

    @orm.db_session
    def test_dicom_fetch_ingestion(self):
        ingestion = schema.Ingestion(
                type=schema.IngestionType.DICOM_FETCH.name,
                accession_number="Anonymous")

        self.assertEqual(ingestion.state, schema.EventState.NEW.name)
        old_reports = orm.count(r for r in schema.Report)

        listener = database_listener.IngestionListener(debug=True)
        listener.run()

        self.assertEqual(ingestion.state, schema.EventState.PROCESSED.name)

        new_reports = orm.count(r for r in schema.Report)
        self.assertGreater(
                new_reports, old_reports,
                "No new Reports created on Ingestion.")


# class ReportListenerTest(unittest.TestCase):
# 
#     @orm.db_session
#     def test_report_simple(self):
#         report = schema.Report.select(lambda r: (
#             r.type == schema.ReportType.PDF_SIMPLE.name and
#             r.state == schema.EventState.PROCESSED.name))[:][0]
# 
#         report.state = schema.EventState.NEW.name
#         orm.commit()
# 
#         reports = schema.Report.get_unprocessed().where(
#                 lambda obj: obj.type == schema.ReportType.PDF_SIMPLE.name)[:]
#         self.assertGreaterEqual(len(reports), 1,
#                 "Expected at least 1 unprocessed PDF_SIMPLE report in test "
#                 "database.")
# 
#         report_listener = database_listener.ReportListener(debug=True)
#         report_listener.run()
# 
#         report = schema.Report[report.id]
#         self.assertEqual(report.state, schema.EventState.PROCESSED.name)
# 

if __name__ == '__main__':
    unittest.main()
