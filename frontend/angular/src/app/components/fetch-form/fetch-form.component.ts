import { Component, OnInit } from '@angular/core';
import { FormControl, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

import { ApiService } from 'src/app/services/api/api.service';

import { environment } from 'src/environments/environment';

interface LookupStudy {
  accession_number: string;
  study_date: string;
  study_description: string;
  patient_name: string;
}

interface FindStudiesResponse {
  studies: LookupStudy[];
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
  foundStudies: LookupStudy[];

  constructor(
    private api: ApiService,
    private fb: FormBuilder,
    private http: HttpClient) {

    this.patientIDForm = fb.group({
      patientID: new FormControl(
        '',
        [Validators.pattern('[a-zA-Z0-9\S]')]),
      studyDate: new FormControl()
    });


    this.fetchForm = fb.group({
      accessionNumber: new FormControl(
        '',
        [Validators.pattern('[a-zA-Z0-9\S]')])
    });
  }

  ngOnInit(): void {
    let now = new Date();
    let dd = String(now.getDate()).padStart(2, '0');
    let mm = String(now.getMonth() + 1).padStart(2, '0'); //January is 0!
    let yyyy = now.getFullYear();
    $('#studyDate').val(mm + '/' + dd + '/' + yyyy);
  }

  submitIDForm(): void {
    this.formSubmitted = true;
    this.formDone = false;
    let patientID = this.patientIDForm.value.patientID;

    let studyDateStr = "";
    let studyDateVal = this.patientIDForm.value.studyDate;
    function yyyymmdd(date: Date) {
        var mm = date.getMonth() + 1; // getMonth() is zero-based
        var dd = date.getDate();

        return [date.getFullYear(),
                    (mm>9 ? '' : '0') + mm,
                    (dd>9 ? '' : '0') + dd
                   ].join('');
    };
    if (studyDateVal) {
      let studyDate = new Date(studyDateVal);
      studyDateStr = yyyymmdd(studyDate);
    }

    // Consider encapsulating in Service if duplication reqiured.
    let url = `${environment.backend_api_url}/api/v1/dicom/find_patient_id/${patientID}/${studyDateStr}`;
    this.http.get<FindStudiesResponse>(url)
      .subscribe((resp: FindStudiesResponse) => {
        this.foundStudies = resp.studies;
        this.formDone = true;
      });
  }

  fetch(event, accessionNumber): void {
    if (event) {
      event.preventDefault();
    }
    $(`#fetch_cell_${accessionNumber}`).text('Sending...');
    this.api.addFetchIngestion(accessionNumber)
      .subscribe(
        resp => window.location.reload(),
        error => this.error = error);
  }

  submitFetchForm(): void {
    this.fetch(null, this.fetchForm.value.accessionNumber);
  }

}
