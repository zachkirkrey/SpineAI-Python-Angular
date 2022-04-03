import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

import { of } from 'rxjs';
import {
  map,
  mergeMap,
  shareReplay
} from 'rxjs/operators';

import { AppSettings } from 'src/app/app.init';
import { UploadService, UploadStatus } from 'src/app/services/upload/upload.service';

import { environment } from 'src/environments/environment';
import {ApiService} from '../../services/api/api.service';
import {v4 as uuidv4} from 'uuid';

declare var $: any;

@Component({
    selector: 'app-intake-form',
    templateUrl: './intake-form.component.html',
    styleUrls: ['./intake-form.component.scss']
})
export class IntakeFormComponent implements OnInit {

    projectName: string;
    @ViewChild('file') file;
    public files: Set<File> = new Set();

    progress;
    // TODO(billy): Make these vars just read from UploadStatus.
    uploading = false;
    uploadSuccessful = false;
    uploadError = false;
    uploadErrorCode: number;

    progressMsg: string;
    // tslint:disable-next-line:variable-name
    study_id: number;
    uploadForm: FormGroup;
    validSexValues: string[] = ['Sex', 'MALE', 'FEMALE'];

    constructor(
        private fb: FormBuilder,
        private router: Router,
        private http: HttpClient,
        private api: ApiService,
        private uploadService: UploadService, private route: ActivatedRoute) {

        this.uploadForm = fb.group({
            // TODO(billy): Enforce validation and create user visible errors.
            projectName: new FormControl('', [Validators.pattern('[a-zA-Z0-9]*')]),
            age: new FormControl(null, [Validators.min(1), Validators.max(120)]),
            height: new FormControl(null, [Validators.min(1), Validators.max(108)]),
            sex: new FormControl(null)
        });
        this.uploadForm.controls['sex'].setValue('Sex');
        this.study_id = this.route.snapshot.params.studty_id;
        console.log('study_id', this.study_id)
    }

    onFilesAdded() {
        const files: { [key: string]: File } = this.file.nativeElement.files;
        for (let key in files) {
            if (!isNaN(parseInt(key))) {
                this.files.add(files[key]);
            }
        }
    }

    uploadFiles() {
        this.projectName = this.uploadForm.value.projectName;
        // TODO(billy): Encapuslate upload and render components in a intake-form
        // that displays both of them to enable a smooth transition/animation
        // between them. (Instead of using the router to jump components)
        this.progressMsg = "Uploading files...";
        this.uploading = true;
        this.uploadService.getUploadStatus().subscribe(uploadStatus => {
            if (uploadStatus == UploadStatus.STARTING_UPLOAD ||
                uploadStatus == UploadStatus.UPLOADING) {
            } else if (uploadStatus == UploadStatus.UPLOAD_ERROR) {
                this.uploadError = true;
                this.uploadService.getUploadErrorCode().subscribe(errorCode => {
                    this.uploadErrorCode = errorCode;
                });
            } else if (uploadStatus == UploadStatus.UPLOAD_COMPLETE) {
                this.uploadSuccessful = true;
                this.uploadService.getUploadId().subscribe(uploadID => {
                    this.waitForReport(uploadID);
                });
            }
        });

        const studyId$ = this.study_id ? of(this.study_id) : this.api.addPatient({
          created_by: true,
          creation_datetime: new Date().toISOString(),
          name: this.projectName,
          file_dir_path: '',
          file_dir_checksum: '',
          image_file_type: '',
          accession_number: '',
          patient_age: '',
          patient_name: this.projectName,
          patient_size: '',
          patient_sex: '',
          study_instance_uid: '',
          mrn: uuidv4(),
          email: '',
          date_of_birth: '',
          phone_number: 0,
          diagnosis: '',
          appointment_date: ''
        }).pipe(
          shareReplay(),
          map(study => {
            this.study_id = study.id;
            return study.id;
          }),
        );

        this.progress = studyId$.pipe(
          mergeMap(
            studyId => this.uploadService
              .upload(this.files, this.uploadForm.value, studyId)
          ),
          shareReplay(),
        );

        this.progress.subscribe((progress) => {
            if (progress >= 99) {
                this.progressMsg = 'Ingesting Study...';
            }
        });
        return false;
    }

    waitForReport(uploadID) {
        this.router.navigate(['studies']);
    }

    ngOnInit() {
    }

    ngAfterViewInit() {
        // Initialize Dropify (file upload) widgets.
        $('.dropify').dropify();
        $('.dropify-wrapper .dropify-message .file-icon p').css('font-size', '15px');
    }

    tryAgain() {
        location.reload();
    }
}
