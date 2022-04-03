"""Client library for DICOM API."""

import logging
import os

from pydicom.dataset import Dataset
import pynetdicom

class DicomClient(object):

    def __init__(self, host, port, aet='THESEUSAI'):
        self.ae_host = host
        self.ae_port = port
        self.ae_title = aet

    def __enter__(self):
        if self.associate():
            return self

        raise RuntimeError(
                f'Could not associate with AE {self.ae_host}:{self.ae_port}')

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.ae_association.release()

    def associate(self):
        self.ae = pynetdicom.AE()
        self.ae.ae_title = self.ae_title
        self.ae.add_requested_context(
                pynetdicom.sop_class.PatientRootQueryRetrieveInformationModelFind)
        self.ae.add_requested_context(
                pynetdicom.sop_class.StudyRootQueryRetrieveInformationModelFind)
        self.ae.add_requested_context(
                pynetdicom.sop_class.PatientRootQueryRetrieveInformationModelMove)
        self.ae.add_requested_context(
                pynetdicom.sop_class.StudyRootQueryRetrieveInformationModelMove)
        self.ae_association = self.ae.associate(self.ae_host, self.ae_port)
        if self.ae_association.is_established:
            return True
        else:
            logging.error(
                    'DICOM AE association rejected, aborted, or never '
                    'connected.')

        return False

    def release(self):
        self.ae_association.release()

    def find(self, dataset):
        """
        Args:
            dataset (pydicom.dataset.Dataset)
        """
        responses = self.ae_association.send_c_find(
                dataset,
                pynetdicom.sop_class.PatientRootQueryRetrieveInformationModelFind)

        identifiers = []

        for (status, identifier) in responses:
            # See http://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_CC.2.8.4.html
            if status.Status == 0:
                # Successful completion.
                pass
            elif status.Status == 0xFF00 or status.Status == 0xFF01:
                identifiers.append(identifier)
            else:
                # Failure or cancel.
                # TODO(billy): Log errors.
                pass

        return identifiers

    def find_by_accession_number(self, accessionNumber):
        ds = self._get_study_dataset()
        ds.AccessionNumber = accessionNumber

        return self.find(ds)

    def find_by_patient_id(self, patient_id, study_date=None):
        """
        Args:
            patient_id: (str)
            study_date: (str) YYYYMMDD
        """
        ds = self._get_study_dataset()
        ds.PatientID = patient_id
        #ds.StudyDescription = "*MR*LUMBAR*"
        ds.Modality = "MR"

        if study_date:
            ds.StudyDate = study_date

        return self.find(ds)

    def move(self, dataset, aet):
        """
        Args:
            dataset (pydicom.dataset.Dataset)
        """
        responses = self.ae_association.send_c_move(
                dataset,
                aet,
                pynetdicom.sop_class.StudyRootQueryRetrieveInformationModelMove)

        identifiers = []

        for (status, identifier) in responses:
            # See http://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_CC.2.8.4.html
            if status.Status == 0:
                # Successful completion.
                pass
            elif status.Status == 0xFF00 or status.Status == 0xFF01:
                identifiers.append(identifier)
            else:
                # Failure or cancel.
                # TODO(billy): Log errors.
                pass

        return identifiers

    def move_by_accession_number(self, accessionNumber, aet):
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.AccessionNumber = accessionNumber

        return self.move(ds, aet)

    def move_by_study_instance_uid(self, studyUID, aet):
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.StudyInstanceUID = studyUID

        return self.move(ds, aet)

    def _get_study_dataset(self):
        """Dataset containing common Study attributes."""

        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'

        ds.AccessionNumber = ''
        ds.StudyDate = ''
        ds.StudyDescription = ''
        ds.StudyID = ''
        ds.StudyInstanceUID = ''
        ds.PatientBrithDate = ''
        ds.PatientID = ''
        ds.PatientSex = ''
        ds.PatientName = ''
        ds.ReferringPhysicianName = ''
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'

        return ds


class DicomStorageServer(object):

    def __init__(self, aet, port, storage_path):
        self.ae = pynetdicom.AE()
        self.ae.ae_title = aet
        self.port = port

        storage_sop_classes = [
                cx.abstract_syntax for cx in pynetdicom.AllStoragePresentationContexts
        ]
        for uid in storage_sop_classes:
            self.ae.add_supported_context(uid, pynetdicom.ALL_TRANSFER_SYNTAXES)

        if not storage_path:
            raise ValueError('Empty storage_path for DicomStorageServer')
        if not os.access(storage_path, os.W_OK | os.X_OK):
            raise RuntimeError(f'Cannot write to {storage_path}.')
        self.storage_path = storage_path

    def handle_store(self, event):
        # Implementation inspired by:
        # https://pydicom.github.io/pynetdicom/stable/examples/qr_move.html
        # and
        # https://pydicom.github.io/pynetdicom/stable/tutorials/create_scp.html
        ds = event.dataset

        study_uid = ds.StudyInstanceUID
        write_path = os.path.join(self.storage_path, study_uid)
        if not os.path.exists(write_path):
                os.mkdir(write_path)

        ds.file_meta = event.file_meta
        ds.save_as(
                os.path.join(write_path, ds.SOPInstanceUID),
                write_like_original=False)

        return 0x0000

    def __enter__(self):
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop_server()

    def start_server(self):
        handlers = [
                (pynetdicom.evt.EVT_C_STORE, self.handle_store)
        ]
        logging.info(f'Starting DICOM server on port {self.port}')
        self.ae.start_server(
                address=('', self.port),
                block=False,
                evt_handlers=handlers)

    def stop_server(self):
        try:
            self.ae.shutdown()
        except Exception as e:
            pass

