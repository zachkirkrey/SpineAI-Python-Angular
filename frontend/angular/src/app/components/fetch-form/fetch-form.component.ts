import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormControl, FormGroup, Validators} from '@angular/forms';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {ApiService, LookupStudy} from 'src/app/services/api/api.service';
import {ActivatedRoute, Router} from '@angular/router';
import {catchError, map, switchMap, tap} from 'rxjs/operators';
import {Observable, of} from 'rxjs';
import {v4 as uuidv4} from 'uuid';

function yyyymmdd(date: Date) {
  const mm = date.getMonth() + 1; // getMonth() is zero-based
  const dd = date.getDate();

  return [date.getFullYear(),
    (mm > 9 ? '' : '0') + mm,
    (dd > 9 ? '' : '0') + dd
  ].join('');
}

@Component({
    selector: 'app-fetch-form',
    templateUrl: './fetch-form.component.html',
    styleUrls: ['./fetch-form.component.scss']
})
export class FetchFormComponent implements OnInit {

    fetchForm: FormGroup;
    patientIDForm: FormGroup;
    error: HttpErrorResponse;
    response: any;

    formSubmitted = false;
    formDone = false;
    foundStudies: LookupStudy[] = [];
    uuidId?: string;
  // tslint:disable-next-line:variable-name
    action_error: any;
    readonly = false;

    constructor(
        private api: ApiService,
        private fb: FormBuilder,
        private http: HttpClient,
        private router: Router,
        private route: ActivatedRoute,
    ) {

        this.patientIDForm = fb.group({
            patientID: new FormControl(
                '',
                [Validators.pattern(/([a-zA-Z0-9\S])+/)]),
            studyDate: new FormControl()
        });

        this.fetchForm = fb.group({
            accessionNumber: new FormControl(
                '',
                [Validators.pattern(/([a-zA-Z0-9\S])+/)])
        });
    }

    ngOnInit(): void {
      const now = new Date();
      const dd = String(now.getDate()).padStart(2, '0');
      const mm = String(now.getMonth() + 1).padStart(2, '0'); // January is 0!
      const yyyy = now.getFullYear();
      $('#studyDate').val(mm + '/' + dd + '/' + yyyy);

      this.uuidId = this.route.snapshot.params.fetch_id;

      if (this.uuidId !== undefined) {
        this.readonly = true;
        this.api.searchPacs(this.uuidId)
          .pipe(
            tap(study => {
              this.patientIDForm.get('patientID').setValue(study.mrn);
              this.fetchForm.get('accessionNumber').setValue(study.accession_number);
            }),
            catchError((err, caught) => {
              this.action_error = err.message ?? err.error;
              return caught;
            })
          )
          .subscribe();
      }
    }

    submitIDForm(): void {
        this.formSubmitted = true;
        this.formDone = false;
        const patientID = this.patientIDForm.value.patientID;

        let studyDateStr = '';
        const studyDateVal = this.patientIDForm.value.studyDate;
        if (studyDateVal) {
            studyDateStr = yyyymmdd(new Date(studyDateVal));
        }

        this.api.findStudies(patientID, studyDateStr)
            .subscribe((studies) => {
                this.foundStudies = studies;
                this.formDone = true;
            });
    }

    async fetch(event, accessionNumber, name = ''): Promise<void> {
      if (event) {
        event.preventDefault();
      }
      $(`#fetch_cell_${accessionNumber}`).text('Sending...');

      const patientID = this.patientIDForm.value.patientID;

      // TODO: now that a relation exists between a study and an ingestion based on the study column
      // ensure linking happens in the creation step
      // additionally, ensure no duplicates
      const uuid$: Observable<string> = this.uuidId ? of(this.uuidId) : this.api.addPatient({
        created_by: true,
        creation_datetime: new Date().toISOString(),
        name,
        file_dir_path: '',
        file_dir_checksum: '',
        image_file_type: '',
        accession_number: '',
        patient_age: '',
        patient_name: name,
        patient_size: '',
        patient_sex: '',
        study_instance_uid: '',
        mrn: patientID,
        email: '',
        date_of_birth: '',
        phone_number: 0,
        diagnosis: '',
        appointment_date: ''
      }).pipe(
        map(study => {
          return study.uuid;
        }),
      );

      uuid$.pipe(
        switchMap(uuid => {
          return this.api.addFetchIngestion({
            accession_number: accessionNumber,
            uuid,
            name,
          });
        })
      ).subscribe(
          (ingestion) => this.router.navigate(['/fetch', ingestion.uuid]),
          error => this.error = error);
    }

    submitFetchForm(): void {
        this.fetch(null, this.fetchForm.value.accessionNumber);
    }

}
