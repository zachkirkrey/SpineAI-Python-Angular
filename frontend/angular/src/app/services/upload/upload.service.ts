import { Injectable } from '@angular/core';
import {
    HttpClient,
    HttpErrorResponse,
    HttpEventType,
    HttpRequest,
    HttpResponse
} from '@angular/common/http';

import { Observable, Subject, throwError } from 'rxjs';
import {catchError, shareReplay} from 'rxjs/operators';

import { environment } from 'src/environments/environment';
const api_url = environment.api_url;
const url = '/upload';

export enum UploadStatus {
    UNKNOWN,
    STARTING_UPLOAD,
    UPLOADING,
    UPLOAD_ERROR,
    UPLOAD_COMPLETE
}

export interface UploadResponse {
    id: string;
}

@Injectable({
    providedIn: 'root'
})
export class UploadService {

    constructor(private http: HttpClient) { }

    // Note we assume one upload per session.
    private _uploadStatus = new Subject<UploadStatus>();
    private _uploadErrorCode = new Subject<number>();
    private _uploadID = new Subject<string>();

    public getUploadStatus() {
        return this._uploadStatus.asObservable();
    }

    public setUploadStatus(newStatus: UploadStatus) {
        this._uploadStatus.next(newStatus);
    }

    public getUploadErrorCode() {
        return this._uploadErrorCode.asObservable();
    }

    public complete() {
        this._uploadStatus.complete();
        this._uploadID.complete();
    }

    public getUploadId() {
        return this._uploadID.asObservable();
    }

    public handleError(error: HttpErrorResponse) {
        this.setUploadStatus(UploadStatus.UPLOAD_ERROR);
        this._uploadErrorCode.next(error.status);
        this.complete();
        console.log(error);
        return throwError('Error uploading files.');
    }

    public upload(files: Set<File>, values, studty_id): Observable<number> {
        this.setUploadStatus(UploadStatus.STARTING_UPLOAD);

        const formData: FormData = new FormData();
        files.forEach(file => {
            formData.append('file', file, file.name);
        });
        for (let key in values) {
            formData.append(key, values[key]);
        };
        formData.append('study', studty_id);
        const req = new HttpRequest('POST', url, formData, {
            reportProgress: true
        });

        const progress = new Subject<number>();
        this.http.request(req)
            .pipe(
                shareReplay(),
                catchError(this.handleError.bind(this)),
            )
            .subscribe(event => {
                if (event.type === HttpEventType.UploadProgress) {
                    this.setUploadStatus(UploadStatus.UPLOADING);
                    const percentDone = Math.round(
                        100 * event.loaded / event.total);
                    progress.next(percentDone);
                } else if (event instanceof HttpResponse) {
                    this.setUploadStatus(UploadStatus.UPLOAD_COMPLETE);
                    let response = event.body as UploadResponse;
                    this._uploadID.next(response.id);
                    progress.complete();
                    this.complete();
                }
            });

        return progress.asObservable();
    }
}
