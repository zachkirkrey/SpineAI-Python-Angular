"""Library for running a HTTP API."""

# We use http.server even though it is not recommended for production.
# No clear lightweight API library was found. FastAPI came closest but
# requires to be run in the main thread by uvicorn.
#
# TODO(billy): Consider finding a more production ready HTTP Server.
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import re
import threading

from config2.config import config

from lib import dicom_client_lib


class APIRequestHandler(object):

    def __init__(self):
        pass

    def find_patient_id(self, mrn, study_date=None):
        response = {}
        response['studies'] = []

        if mrn:
            with dicom_client_lib.DicomClient(
                    config.spineai.dicom.remote_ae_host,
                    config.spineai.dicom.remote_ae_port,
                    config.spineai.dicom.aet) as client:
                results = client.find_by_patient_id(mrn, study_date)

            for result in results:
                patient_name = result.PatientName

                study = {
                    'accession_number': result.AccessionNumber,
                    'study_date': result.StudyDate,
                    'study_description': result.StudyDescription,
                    'patient_name': f'{patient_name.family_name}, {patient_name.given_name}'
                }
                response['studies'].append(study)

        return response

    def handle_request(self, path):
        response_obj = None

        if re.search('/api/v1/dicom/.*', path):
            p = re.compile('/api/v1/dicom/find_patient_id/(.*)')
            match = p.search(path)
            if match:
                query = match.group(1)

                patient_id = query
                study_date = None

                p = re.compile('(.*)/(.*)')
                match = p.search(query)
                if match:
                    patient_id = match.group(1)
                    study_date = match.group(2)

                print(study_date)
                response_obj = self.find_patient_id(patient_id, study_date)

        if not response_obj:
            response_obj = {
                'error': f'Could not find handler for path {path}'
            }

        return json.dumps(response_obj)


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super(HTTPRequestHandler, self).__init__(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()

        request_handler = APIRequestHandler()
        response = request_handler.handle_request(self.path)
        self.wfile.write(response.encode())


class APIServer(object):

    def __init__(self, addr='', port='8008'):
        self.addr = addr
        self.port = port

        self.httpd = HTTPServer((addr, port), HTTPRequestHandler)

        self.is_started = False

    def run(self):
        logging.info(f'Starting API server on {self.addr}:{self.port}')
        self.is_started = True
        self.httpd.serve_forever()

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop_thread(self):
        self.httpd.shutdown()
        self.thread.join()
