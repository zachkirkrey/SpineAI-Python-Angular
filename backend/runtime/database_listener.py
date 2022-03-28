"""Library for listening for and processing SQL database events."""

import base64
import datetime
import logging
import os
import shutil
import tempfile
import threading
import time
import zipfile

from config2.config import config
from pony import orm

from lib import classifier_lib
from lib import dicom_client_lib
from lib import report_lib
from runtime import study_reader

from lib import schema

# A magic thread that propagates Exceptions, from
# https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread
class PropagatingThread(threading.Thread):
    def run(self):
        self.exc = None
        try:
            if hasattr(self, '_Thread__target'):
                # Thread uses name mangling prior to Python 3.
                self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            else:
                self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super(PropagatingThread, self).join(timeout)
        if self.exc:
            raise self.exc
        return self.ret


class AbstractListener(object):

    def __init__(self, schema_class, debug):
        if not schema_class:
            raise ValueError('No schema_class specified.')

        self.debug = debug
        self.schema_class = schema_class


    def process(self, event):
        return NotImplementedError()

    @orm.db_session
    def _process_event_id(self, event_id):
        """Processes the event for a given database object ID.

        We fetch the event again here to allow this function to run inside its
        own thread.
        """
        event = self.schema_class[event_id]
        self.process(event)

    def _process(self, events):
        for event in events:
            event.state = schema.EventState.QUEUED.name
        orm.commit()

        for event in events:
            event.state = schema.EventState.PROCESSING.name
            orm.commit()

            try:
                event.started_datetime = datetime.datetime.now()

                # Process the underlying event in a child thread to prevent memory leaks.
                event_thread = PropagatingThread(
                        target=self._process_event_id, args=(event.id,))
                event_thread.start()
                event_thread.join()

                event.completed_datetime = datetime.datetime.now()
                event.state = schema.EventState.PROCESSED.name
            except Exception as e:
                if self.debug:
                    raise e
                logging.error(
                    'Error processing {} id "{}": {}: "{}"'.format(
                        self.schema_class.__name__, event.id, type(e), str(e)))
                event.state = schema.EventState.ERROR.name
                event.error_str = str(e)

    def run(self):
        """Find and process unprocessed Events in the database."""

        with orm.db_session(optimistic=False):
            events = self.schema_class.get_unprocessed().order_by(
                self.schema_class.creation_datetime)[:]

            if len(events):
                logging.info(
                    'Discovered {} unprocessed {}s. '
                    'Processing ...'.format(
                        len(events),
                        self.schema_class.__name__))
            else:
                logging.debug('No incomplete {}s discovered.'.format(
                    self.schema_class.__name__))

            self._process(events)


class IngestionListener(AbstractListener):
    """This class processes Reports in the database."""

    def __init__(self, *args, **kwargs):
        AbstractListener.__init__(self,
                schema_class=schema.Ingestion, *args, **kwargs)
        self.study_reader = study_reader.StudyReader(
                debug=self.debug,
                report_types=config.spineai.report.types)

        logging.info('Creating DICOM server.');
        self.tmpdir = tempfile.TemporaryDirectory()
        self.dicom_server = dicom_client_lib.DicomStorageServer(
                config.spineai.dicom.aet,
                config.spineai.dicom.listen_port,
                self.tmpdir.name)
        self.dicom_server.start_server()

        self.study_reader = study_reader.StudyReader(
                do_classify = config.spineai.classification.settings.do_classify,
                report_types = config.spineai.report.types)

    def __del__(self):
        self.dicom_server.stop_server()
        self.tmpdir.cleanup()

    def process(self, ingestion):
        # TODO(billy): Make this a configurable directory so we save raw files.
        if ingestion.type == schema.IngestionType.DICOM_FETCH.name:
            if not ingestion.accession_number:
                raise ValueError(
                        f'Empty accession_number for Ingestion {ingestion.uuid}')
            with dicom_client_lib.DicomClient(
                    config.spineai.dicom.remote_ae_host,
                    config.spineai.dicom.remote_ae_port,
                    config.spineai.dicom.aet) as client:
                results = client.find_by_accession_number(
                        ingestion.accession_number)
                if not results:
                    raise ValueError(
                            f'No results for accession_number {ingestion.accession_number}.')

                study_uid = results[0].StudyInstanceUID

                results = client.move_by_study_instance_uid(
                        study_uid,
                        config.spineai.dicom.aet)

            if study_uid in os.listdir(self.tmpdir.name):
                study_dir = os.path.join(self.tmpdir.name, study_uid)
                study = self.study_reader.ingest_study(
                        study_dir, name=ingestion.accession_number)

                shutil.rmtree(study_dir, ignore_errors=True)

        elif ingestion.type == schema.IngestionType.FILE_BYTES.name:
            with tempfile.TemporaryFile('w+b') as f:
                f.write(base64.b64decode(
                    ingestion.file_archive_bytes, validate=True))
                f.seek(0)
                with tempfile.TemporaryDirectory() as tempdir:
                    with zipfile.ZipFile(f) as zipf:
                        zipf.extractall(tempdir)
                        self.study_reader.ingest_study(
                                tempdir,
                                name=ingestion.name,
                                study_id=2)
        else:
            raise ValueError(
                    f'Ingestion {ingestion.uuid}: Unknown ingestion type {ingestion.type}')


class ClassificationListener(AbstractListener):
    """This class processes Classifications in the database."""

    def __init__(self, *args, **kwargs):
        AbstractListener.__init__(self,
                schema_class=schema.Classification, *args, **kwargs)
        self.classifier_registry = classifier_lib.get_default_registry()
        self._update_versions()

    def _update_versions(self):
        with orm.db_session():
            old_classifications = self.schema_class.select(
                    lambda c: c.version != classifier_lib.CLASSIFICATION_VERSION)
            for c in old_classifications:
                c.version = classifier_lib.CLASSIFICATION_VERSION
                c.state = schema.EventState.NEW.value

                # If we reprocess Classifications, we must reprocess Reports
                # as well.
                reports = schema.Report.select(
                        lambda r: c in r.input_classifications)
                for r in reports:
                    r.state = schema.EventState.NEW.value

    def process(self, classification):
        self.classifier_registry.process(classification)


class ReportListener(AbstractListener):
    """This class processes Reports in the database."""

    def __init__(self, *args, **kwargs):
        AbstractListener.__init__(self,
                schema_class=schema.Report, *args, **kwargs)
        self._update_versions()

    def _update_versions(self):
        with orm.db_session():
            for report_type in report_lib.REPORT_VERSIONS:
                old_reports = self.schema_class.select(
                        lambda r: r.type == report_type and r.version != report_lib.REPORT_VERSIONS[report_type])

                for r in old_reports:
                    r.version = report_lib.REPORT_VERSIONS[report_type]
                    r.state = schema.EventState.NEW.value

    def process(self, report):
        report.process()


class DatabaseListener(object):

    # TODO(billy): Make constants configurable via .yml
    def __init__(self, sleep_secs=5, debug=False, daemon=True):
        """
        Args:
            sleep_secs: (int) Seconds to sleep between looking for new events.
            debug: (bool) Debug value to pass to underlying Listeners. Causes
                listner to raise instead of log exceptions.
            daemon: (bool) If False, exit after one database query iteration.
        """
        self.sleep_secs = sleep_secs
        self.daemon = daemon
        self.listeners = [
            IngestionListener(debug=debug),
            ClassificationListener(debug=debug),
            ReportListener(debug=debug)
        ]

    def run(self):
        """Blocking call that runs Listeners on the database."""
        while True:
            # TOOD(billy): Run these listeners in separate threads to avoid
            # blocking.
            for listener in self.listeners:
                listener.run()
            if not self.daemon:
                return

            time.sleep(self.sleep_secs)


