import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import {Observable, of} from 'rxjs';
import {map} from 'rxjs/operators';
import { v4 as uuidv4 } from 'uuid';

import { environment } from 'src/environments/environment';

// TODO(billy): Use JSON Schema to generate this interface.
interface CanalHeight {
    origin: Array<number>;
    px_height: number;
    display_height: number;
    unit: string;
}
interface CanalWidth {
    origin: Array<number>;
    px_width: number;
    display_height: number;
    unit: string;
}
interface GeisingerMeasurements {
    canal_heights: Array<CanalHeight>;
    canal_widths: Array<CanalWidth>;
}

interface CanalNarrowingMeasurements {
    num_narrow_slices?: number;
    surgery_recommended?: boolean;
}

interface Measurements {
    geisinger: GeisingerMeasurements;
    canal_narrowing: CanalNarrowingMeasurements;
}

interface CanalSegmentation {
    all_canal_areas: Array<number>;
    canal_areas: Array<number>;
    canal_expected_areas: Array<number>;
}

export interface Ingestion {
    uuid: string;
    creation_datetime: string;
    state: string;
    accession_number: string;
    error_str: string;
    name: string;
    type: string;
}

export interface JSONReport {
    report_date: string;
    measurements: Measurements;
    canal_segmentation: CanalSegmentation;
}

export interface Study {
  id: number;
  uuid: string;
  name: string;
  creation_datetime: string | Date;
  file_dir_path: string;
  file_dir_checksum: string;
  accession_number: string;
  patient_age: string;
  patient_name: string;
  patient_size: string;
  patient_sex: string;
  study_instance_uid: string;
  image_file_type: string;
  mrn: string;
  email: string;
  date_of_birth: string | Date;
  phone_number: number;
  diagnosis: string;
  created_by: boolean;
  appointment_date: string | Date;
}

export interface Report {

  id: number;
  uuid: string;
  state: string;
  type: string;
  creation_datetime: string | Date;
  started_datetime: string | Date;
  completed_datetime: string | Date;
  error_str: string;
  num_narrow_slices: number;
  surgery_recommended: boolean;
}

export interface Action {
  id: number;
  name: string;
  creation_datetime: string | Date;
  study: number;
}

export interface StudyWithActions extends Study {
  Actions: Action[];
  Reports: Report[];
}

// export interface Patient {
//
// }

export interface LookupStudy {
  accession_number: string;
  study_date: string;
  study_description: string;
  patient_name: string;
}

export interface FindStudiesResponse {
  studies: LookupStudy[];
}

export function local(): boolean {
  return !!window.location.host.match(/localhost/);
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {

    apiUrl = environment.api_url;
    token: any;

    constructor(
        private http: HttpClient) {
        this.token = localStorage.getItem('token');
    }

    private options() {
      return {headers: { Authorization: 'Bearer ' + this.token } };
    }

    getStudy(uuid: string, scope: string) {
        let queryParams = '?';
        if (scope) {
            queryParams += `scope=${scope}`;
        }
        // TODO(billy): Create interfaces for these types.
        return this.http.get<any>(
            `${this.apiUrl}/study/${uuid}${queryParams}`, this.options());
    }

    getReport(uuid: string, as?: string) {
        if (as && as.toLowerCase() === 'json') {
            const queryParams = `?as=${as}`;
            return this.http.get<JSONReport>(
                `${this.apiUrl}/report/${uuid}${queryParams}`, this.options());
        }
        return this.http.get<any>(
            `${this.apiUrl}/report/${uuid}`, this.options());
    }

    getReportJsonFromStudy(study) {
        const reports = study.Reports;

        let latestDate = new Date(1970, 0, 1);
        let reportUuid = null;
        reports.forEach((report) => {
            const reportCreated = new Date(report.creation_datetime);
            if (report.type == 'JSON' &&
                reportCreated > latestDate) {
                latestDate = reportCreated;
                reportUuid = report.uuid;
            }
        });

        return this.getReport(reportUuid, 'json');
    }

    getReportJsonFromStudyId(studyUuid: string) {
        return new Observable<JSONReport>(subscriber => {
            this.getStudy(studyUuid, 'deep').subscribe(study => {
                this.getReportJsonFromStudy(study).subscribe(report => {
                    subscriber.next(report);
                    subscriber.complete();
                });
            });
        });
    }

    getImageLinksFromSeries(series) {
        const sliceUrls = {};
        let num_slices = 0;

        series.Images.forEach((image) => {
            sliceUrls[image.slice] = `${this.apiUrl}/image/${image.uuid}?as=img`;
            num_slices += 1;
        });

        const images = [];
        for (let i = 0; i < num_slices; i++) {
            images.push(sliceUrls[i]);
        }
        return images;
    }

    getPacIngestions(uuid) {
         return this.http.get<any>(`${this.apiUrl}/ingestions?type=DICOM_FETCH`, this.options());
    }

    getStudyActions(studyId): Observable<Action[]> {
      return this.http.get<Action[]>(`${this.apiUrl}/action?study=${studyId}`, this.options());
    }

    addStudyAction(studyId, action: Omit<Action, 'id' | 'creation_datetime' | 'study'>): Observable<Action> {
      return this.http.post<Action>(`${this.apiUrl}/action`, {
        ...action,
        study: studyId,
        creation_datetime: new Date().toISOString(),
      } as Action, this.options());
    }

    getFetchIngestions(uuid) {
         return this.http.get<Ingestion[]>(`${this.apiUrl}/ingestions?uuid=${uuid}`, this.options());
    }

    addPatient(data: Omit<Study, 'id' | 'uuid'>): Observable<Study> {
      return this.http.post<Study>(`${this.apiUrl}/studies`, {
        uuid: uuidv4(),
        ...data
      });
    }

    addFetchIngestion(data: Omit<Ingestion, 'creation_datetime' | 'uuid' | 'type' | 'state' | 'error_str'>): Observable<Ingestion> {
         const date = new Date();
         const ingestion: Ingestion = {
           ...data,
            creation_datetime: date.toISOString(),
            type: 'DICOM_FETCH',
            state: 'NEW',
            uuid: uuidv4(),
            error_str: '',
        };

         return this.http.post<Ingestion>(
            `${this.apiUrl}/ingestions`,
            ingestion, this.options());
    }

    searchPacs(uuid: string): Observable<Study>  {
      return this.http.post<Study>(`${this.apiUrl}/search/pacs`, {uuid}, this.options());
    }

    findStudies(patientID: string, studyDateStr: string): Observable<LookupStudy[]> {

      // // Local simulated patient data
      // if (local()) {
      //   return of([
      //     {
      //       accession_number: uuidv4(),
      //       patient_name: 'Example Patient',
      //       study_date: new Date().toISOString(),
      //       study_description: 'Something goes here',
      //     },
      //     {
      //       accession_number: uuidv4(),
      //       patient_name: 'Example Patient 2',
      //       study_date: new Date().toISOString(),
      //       study_description: 'Something else goes here',
      //     },
      //   ]);
      // }

      const url = `${environment.backend_api_url}/api/v1/dicom/find_patient_id/${patientID}/${studyDateStr}`;
      return this.http.get<FindStudiesResponse | null>(url, this.options()).pipe(
        map(resp => resp?.studies ?? [])
      );
    }

    // findPatients(patientID: string) : Observable<Patient[]> {
    //   const url = `${environment.backend_api_url}/api/v1/dicom/find_patient_id/${patientID}/${studyDateStr}`;
    //   return this.http.get<FindStudiesResponse | null>(url, this.options()).pipe(
    //     map(resp => resp?.studies ?? [])
    //   );
    // }

    globalGetRequest(endpoint: string){
      const url = `${this.apiUrl}/${endpoint}`;
      return this.http.get(url, this.options());
    }

    globalGetMore(endpoint: string){
      return this.http.get(endpoint, this.options());
    }

    globalPostRequest(endpoint: string, data: any){
      const url = `${this.apiUrl}/${endpoint}`;
      return this.http.post(url, data, this.options());
    }

    globalPatchRequest(endpoint: string, data: any){
      const url = `${this.apiUrl}/${endpoint}`;
      return this.http.patch(url, data, this.options());
    }

    globalDeleteRequest(endpoint: string){
      const url = `${this.apiUrl}/${endpoint}`;
      return this.http.delete(url, this.options());
    }
}
