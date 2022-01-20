import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';
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

interface Ingestion {
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

@Injectable({
    providedIn: 'root'
})
export class ApiService {

    apiUrl = environment.api_url;
    token: any

    constructor(
        private http: HttpClient) {
        this.token = localStorage.getItem('token')
    }

    getStudy(uuid: string, scope: string) {
        const headers = { "Authorization": 'Bearer ' + this.token }
        let queryParams = '?';
        if (scope) {
            queryParams += `scope=${scope}`;
        }
        // TODO(billy): Create interfaces for these types.
        return this.http.get<any>(
            `${this.apiUrl}/study/${uuid}${queryParams}`, { 'headers': headers });
    }

    getReport(uuid: string, as?: string) {
        const headers = { "Authorization": 'Bearer ' + this.token }
        if (as && as.toLowerCase() == 'json') {
            let queryParams = `?as=${as}`;
            return this.http.get<JSONReport>(
                `${this.apiUrl}/report/${uuid}${queryParams}`, { 'headers': headers });
        }
        return this.http.get<any>(
            `${this.apiUrl}/report/${uuid}`, { 'headers': headers });
    }

    getReportJsonFromStudy(study) {
        let reports = study.Reports;

        let latestDate = new Date(1970, 0, 1);
        let reportUuid = null;
        reports.forEach((report) => {
            let reportCreated = new Date(report.creation_datetime);
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
                })
            })
        });
    }

    getImageLinksFromSeries(series) {
        let sliceUrls = {};
        let num_slices = 0;

        series.Images.forEach((image) => {
            sliceUrls[image.slice] = `${this.apiUrl}/image/${image.uuid}?as=img`;
            num_slices += 1;
        });

        let images = [];
        for (let i = 0; i < num_slices; i++) {
            images.push(sliceUrls[i]);
        }
        return images;
    }

    getFetchIngestions(uuid) {
        const headers = { "Authorization": 'Bearer ' + this.token }
         this.http.get<any>(`${this.apiUrl}/ingestions?type=DICOM_FETCH`, { 'headers': headers });
        return this.http.get<any>(`${this.apiUrl}/ingestions?uuid=${uuid}`, { 'headers': headers });
    }

    addFetchIngestion(data) {
         var date = new Date();
        let ingestion: Ingestion = {
            uuid: data.uuid,
            creation_datetime: date.toISOString(),
            type: 'DICOM_FETCH',
            state: 'NEW',
            accession_number: data.accessionNumber,
            error_str: '',
            name: ''
        };
        const headers = { "Authorization": 'Bearer ' + this.token }
        return this.http.post<any>(
            `${this.apiUrl}/ingestions`,
            ingestion, { 'headers': headers });
    }
}
