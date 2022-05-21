import { Component, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin, Subject } from 'rxjs';
import { ActionListValues } from 'src/app/helpers/action-list.enum';
import { Action, ApiService } from 'src/app/services/api/api.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-triage',
  templateUrl: './triage.component.html',
  styleUrls: ['./triage.component.scss']
})
export class TriageComponent implements OnInit, OnDestroy {

  readonly api_url = environment.api_url;

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

  users: any[] = [];
  updateStudyForm: FormGroup;
  actionList = ActionListValues;
  todayDate = new Date();
  actions: Action[] = [];
  studyUuid: string = '';
  studyId: number;
  studyLastAction: Action;

  updateLoading: boolean = false;
  updateError: boolean = false;
  updateErrorMessage: string = 'Something went wrong, please try again';
  updateSuccess: boolean = false;

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
    this.getUsers();
    this.getStudies();
    this.createUpdateStudyForm();
  }

  ngOnDestroy(): void {
    this.dtTrigger.unsubscribe();
  }

  getStudies() {
    this.studies = [];
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

  openUpdateApptDialog(content, study: any) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
      
    }, (reason) => {
        
    });
    this.studyUuid = study.uuid;
    this.actions = study.Actions;
    this.studyId = study.id;
    if (study.last_action != null && study.last_action != 'N/A') {
      this.updateStudyForm.controls['last_action'].setValue(study.last_action.name);
    }

    if (study.appointment_date != null && study.appointment_date != 'N/A') {
      this.updateStudyForm.controls['appt_date'].setValue(new Date(study.appointment_date.split('T')[0]));
    }

    if (study.assignee != null) {
      this.updateStudyForm.controls['assignee'].setValue(study.assignee);
    }

    if (study.status != null) {
      this.updateStudyForm.controls['status'].setValue(study.status);
    }
  }

  updateAppointment() {
    this.updateLoading = true;

    const formValue = this.updateStudyForm.value;
    const reqDate = `${formValue.appt_date.getMonth() + 1}/${formValue.appt_date.getDate()}/${formValue.appt_date.getFullYear()}`;
    
    const reqData = {
      appointment_date: new Date(`${reqDate} GMT+00:00`),
      status: formValue.status,
      assignee: formValue.assignee
    };
    let updateStudyData = this._api.globalPatchRequest(`study/${this.studyUuid}`, reqData);

    const updateActionReqData = {
      name: formValue.last_action,
      study: this.studyId
    };
    let updateAction = this._api.globalPostRequest('action', updateActionReqData);
    const lastAction = formValue.last_action;

    let mForkJoin = forkJoin([]);

    if (lastAction != null && lastAction.length > 0) {
      if (this.actions.length > 0) {
        if (lastAction != this.actions[this.actions.length - 1].name) {
          mForkJoin = forkJoin([updateStudyData, updateAction]);
        } else {
          mForkJoin = forkJoin([updateStudyData]);
        }
      } else {
        mForkJoin = forkJoin([updateStudyData, updateAction]);
      }
    } else {
      mForkJoin = forkJoin([updateStudyData]);
    }

    mForkJoin.subscribe((response: any) => {
      this.updateLoading = false;
      this.updateSuccess = true;
    }, (error: any) => {
      console.log(error);
      this.updateLoading = false;
      this.updateError = true;
    });
  }

  dismissDialog() {
    this.modalService.dismissAll();
    this.updateLoading = false;
    this.updateSuccess = false;
    this.updateError = false;
    this.dtTrigger.unsubscribe();
    this.getStudies();
  }

  getUsers() {
    this._api.globalGetRequest(`users`).subscribe((response: any) => {
    this.users = response;
    }, (error: any) => {
        console.log(error);
    });
  }

  createUpdateStudyForm() {
    this.updateStudyForm = this._formBuilder.group({
      last_action: [''],
      appt_date: ['', [Validators.required]],
      assignee: [''],
      status: [''],
    });
  }
}
