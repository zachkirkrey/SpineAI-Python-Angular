import { Component, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { Subject } from 'rxjs';
import { ApiService } from 'src/app/services/api/api.service';

@Component({
  selector: 'app-triage',
  templateUrl: './triage.component.html',
  styleUrls: ['./triage.component.scss']
})
export class TriageComponent implements OnInit, OnDestroy {

  token: any;
  isLoading: boolean = false;
  loadingStudiesError: string;

  studies: any[] = [];
  studiesToDisplay: any [] = [];
  appt_filter: any = '';
  show_Archived: boolean = false;
  show_doneItems: boolean = false;
  patientNameShown: boolean = true;
  section: string = '';
  apptDateList = [
    { name: 'ALL TIME', value: 'all time' }, 
    { name: 'TODAY', value: 'today' }, 
    { name: 'LAST 10 DAYS', value: 'last ten' }, 
    { name: 'NEXT 10 DAYS', value: 'next ten' }, 
    { name: 'NONE', value: 'none' }
  ];

  dtOptions: DataTables.Settings = {};
  dtTrigger: Subject<any> = new Subject<any>();

  @ViewChildren('patients_rows') patients_rows: QueryList<any>;
  constructor(
    private modalService: NgbModal,
    private _api: ApiService,
    private _formBuilder: FormBuilder
  ) { 
    this.token = localStorage.getItem('token');
  }

  ngOnInit(): void {
    this.token = localStorage.getItem('token');
    this.dtOptions = {
      pageLength: 25,
      processing: true
    };
    this.getStudies();
  }

  ngOnDestroy(): void {
    this.dtTrigger.unsubscribe();
  }

  getStudies() {
    this.isLoading = true;
    this._api.globalGetRequest(`studies?scope=includeActions`).subscribe((response: any) => {
      this.isLoading = false;
      response.forEach(element => {
        const actions = element['Actions'];
        if (actions.length > 0) {
          element['last_action'] = actions.at(-1);

          if (actions.length > 1) {
            element['prev_action'] = actions.at(-2);
          } else {
            element['prev_action'] = {
              name: 'N/A',
              creation_datetime: 'N/A'
            }
          }
        } else {
          element['last_action'] = {
            name: 'N/A',
            creation_datetime: 'N/A'
          };
          element['prev_action'] = {
            name: 'N/A',
            creation_datetime: 'N/A'
          }
        };

        this.studies.push(element);
      });
      this.dtTrigger.next();
    }, (error: any) => {
      this.isLoading = false;
      this.loadingStudiesError = error.data.toString();
      console.log(error);
    });

  }

  apptFilter(event) {
    if (this.studies != undefined || this.studies.length > 0) {
        this.appt_filter = event.target.value;
        if (event.target.value == 'today') {
            this.getStudies();
        } else if (event.target.value == 'last ten') {
            this.getStudies();
        } else if (event.target.value == 'next ten') {
            this.getStudies();
        } else if (event.target.value == 'none') {
            this.getStudies();
        } else if (event.target.value == 'all time') {
            this.getStudies();
        }
    }
  }

  showDoneItems(event) {
    if (this.studies != undefined) {
        if (event.checked == true) {
            this.show_doneItems = true
            this.getStudies();
        }
        else {
            this.show_doneItems = false
            this.getStudies();
        }
    }
  }

  showArchived(event) {
    if (this.studies != undefined) {
        if (event.checked == true) {
            this.show_Archived = true
            this.getStudies();
        }
        else {
            this.show_Archived = false
            this.getStudies();
        }
    }
  }

  showPatientName(event) {
    if (event.checked == true) {
      this.patientNameShown = false;
    } else if (event.checked == false) {
      this.patientNameShown = true;
    }
  }

  openUpdateApptDialog(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {

    }, (reason) => {

    });
  }

  updateAppointment() {

  }

  dismissDialog() {
    this.modalService.dismissAll();
  }
}