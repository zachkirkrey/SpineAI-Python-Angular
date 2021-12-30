"""Unit tests for backend_api.py"""

from runtime import backend_api

from testutil import unittest


class ImgLibTest(unittest.TestCase):

    # TODO(billy): Create test with working DICOM server.
    def test_start_server(self):
        api = backend_api.APIServer('', 8008)


if __name__ == '__main__':
    unittest.main()
