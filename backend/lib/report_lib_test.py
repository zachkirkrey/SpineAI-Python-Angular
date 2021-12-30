"""Unit tests for report_lib.py"""

import json
import os
import tempfile
import time

from pony import orm

from testutil import unittest

from lib import report_lib

from lib import schema


class ReportTest(unittest.TestCase):

    # @orm.db_session
    # def test_report_pdf_simple(self):
    #     report = schema.Report(type=schema.ReportType.PDF_SIMPLE.name)
    #     orm.commit()

    #     studies = schema.Study.select()[:]
    #     self.assertGreaterEqual(len(studies), 1)

    #     report.input_studies.add(studies)
    #     for c in studies[0].classifications:
    #         report.input_classifications.add(c)

    #     report.process()

    # @orm.db_session
    # def test_report_html_viewer(self):
    #     report = schema.Report(type=schema.ReportType.HTML_VIEWER.name)
    #     orm.commit()

    #     studies = schema.Study.select()[:]
    #     self.assertGreaterEqual(len(studies), 1)

    #     report.input_studies.add(studies)
    #     for c in studies[0].classifications:
    #         report.input_classifications.add(c)

    #     report.process()

    @orm.db_session
    def test_report_json(self):
        report = schema.Report(type=schema.ReportType.JSON.name)
        orm.commit()

        studies = schema.Study.select()[:]
        self.assertGreaterEqual(len(studies), 1)

        report.input_studies.add(studies)
        for c in studies[0].classifications:
            report.input_classifications.add(c)

        report.process()

        report_str = report.report_bytes.decode('utf-8')
        json_obj = json.loads(report_str)
        self.assertIn('errors', json_obj)
        self.assertEqual(len(json_obj['errors']), 0)




if __name__ == '__main__':
    unittest.main()
