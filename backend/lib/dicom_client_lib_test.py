"""Unittests for dicom_client_lib.py"""

import os
import shutil
import time

from testutil import unittest

from pydicom.dataset import Dataset

from lib import dicom_client_lib

AE_HOST='192.168.4.200'
AE_PORT=4242

LOCAL_STORAGE_DIR = '/tmp/DicomStorageServerTest'

class DicomClientTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO(billy): Set up a test AE server for this unitteest.


    def test_context_manager(self):
        with dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT) as client:
            pass

    def test_associate(self):
        self.dicom_client = dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT)
        self.assertTrue(self.dicom_client.associate())
        self.dicom_client.release()

    def test_find(self):
        with dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT) as client:
            ds = Dataset()
            ds.QueryRetrieveLevel = 'STUDY'
            ds.AccessionNumber = 'Anonymous'

            result = client.find(ds)
            self.assertGreater(len(result), 0)

    def test_find_by_accession_number(self):
        with dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT) as client:
            result = client.find_by_accession_number('Anonymous')
            self.assertGreater(len(result), 0)

    def test_not_find_by_accession_number(self):
        with dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT) as client:
            result = client.find_by_accession_number('DoesntExist')
            self.assertEqual(len(result), 0)

    def test_find_by_patient_id(self):
        with dicom_client_lib.DicomClient(
                host=AE_HOST,
                port=AE_PORT) as client:
            result = client.find_by_patient_id('Anonymous')
            self.assertGreater(len(result), 0)

    def test_move(self):
        if os.path.exists(LOCAL_STORAGE_DIR):
            shutil.rmtree(LOCAL_STORAGE_DIR, ignore_errors=True)
        os.mkdir(LOCAL_STORAGE_DIR)

        # NOTE(billy): For this to pass, the remote server must already "know"
        # about this AET ("billycao").

        with dicom_client_lib.DicomStorageServer(
                aet='THESEUSAI',
                port=11112,
                storage_path=LOCAL_STORAGE_DIR) as server:
            with dicom_client_lib.DicomClient(
                    host=AE_HOST,
                    port=AE_PORT) as client:
                result = client.move_by_accession_number('Anonymous', 'THESEUSAI')
                self.assertGreater(len(result), 0)

            num_dirs = sum(
                    os.path.isdir(os.path.join(LOCAL_STORAGE_DIR, d)) for d in os.listdir(LOCAL_STORAGE_DIR))
            self.assertGreater(num_dirs, 0)

    def testNotMove(self):
        if os.path.exists(LOCAL_STORAGE_DIR):
            shutil.rmtree(LOCAL_STORAGE_DIR, ignore_errors=True)
        os.mkdir(LOCAL_STORAGE_DIR)

        # NOTE(billy): For this to pass, the remote server must already "know"
        # about this AET ("billycao").
        with dicom_client_lib.DicomStorageServer(
                aet='THESEUSAI',
                port=11112,
                storage_path=LOCAL_STORAGE_DIR) as server:
            with dicom_client_lib.DicomClient(
                    host=AE_HOST,
                    port=AE_PORT) as client:
                result = client.move_by_accession_number('DoesntExist', 'THESEUSAI')
                self.assertEqual(len(result), 0)

            num_dirs = sum(
                    os.path.isdir(os.path.join(LOCAL_STORAGE_DIR, d)) for d in os.listdir(LOCAL_STORAGE_DIR))
            self.assertEqual(num_dirs, 0)




class DicomStorageServerTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def testStartServer(self):
        if not os.path.exists(LOCAL_STORAGE_DIR):
            os.mkdir(LOCAL_STORAGE_DIR)
        dicom_server = dicom_client_lib.DicomStorageServer(
                aet='THESEUSAI',
                port=11112,
                storage_path=LOCAL_STORAGE_DIR)
        dicom_server.start_server()
        dicom_server.stop_server()


if __name__ == '__main__':
    # TODO(billy): Enable these unit tests after setting up test DICOM server.
    # unittest.main()
