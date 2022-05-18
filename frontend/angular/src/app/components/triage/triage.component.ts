import { Component, OnInit, QueryList, ViewChildren } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiService } from 'src/app/services/api/api.service';


@Component({
  selector: 'app-triage',
  templateUrl: './triage.component.html',
  styleUrls: ['./triage.component.scss']
})
export class TriageComponent implements OnInit {

  token: any;
  isLoading: boolean = false;
  loadingPatientsError: string;

  patients: any[] = [];
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
    this.tableData();
  }

  ngAfterViewInit() {
    // Ellipsis renderer for datatables.net from
    // https://datatables.net/blog/2016-02-26.
    let render_ellipsis = function (cutoff, ellipsis, wordbreak, escapeHtml) {
        var esc = function (t) {
            return t
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        };

        return function (d, type, row) {
            // Order, search and type get the original data
            if (type !== 'display') {
                return d;
            }

            if (typeof d !== 'number' && typeof d !== 'string') {
                return d;
            }

            d = d.toString(); // cast numbers

            if (d.length < cutoff) {
                return d;
            }

            var shortened = d.substr(0, cutoff - 1);

            // Find the last white space character in the string
            if (wordbreak) {
                shortened = shortened.replace(/\s([^\s]*)$/, '');
            }

            // Protect against uncontrolled HTML input
            if (escapeHtml) {
                shortened = esc(shortened);
            }
            if (ellipsis) {
                return '<span class="ellipsis" title="' + esc(d) + '">' + shortened + '&#8230;</span>';
            }
            return '<span class="ellipsis" title="' + esc(d) + '">' + shortened + '</span>';
        };

    };

    this.patients_rows.changes.subscribe(t => {
        $('#patients_table').DataTable({
            retrieve: true,
            pageLength: 25,
            order: [[0, 'desc']],
            columnDefs: [{
                // Only render date component of Created.
                targets: 0,
                render: render_ellipsis(11, false, false, false)
            }, {
                // Render Study UID with ellipsis.
                targets: 2,
                render: render_ellipsis(15, true, false, false)
            }],
            destroy: true
        });
    });

    $('#patients_table').DataTable({
      retrieve: true,
      pageLength: 25,
      order: [[0, 'desc']],
      columnDefs: [{
          // Only render date component of Created.
          targets: 0,
          render: render_ellipsis(11, false, false, false)
      }, {
          // Render Study UID with ellipsis.
          targets: 2,
          render: render_ellipsis(15, true, false, false)
      }],
      destroy: true
    });
  }

  tableData() {
    this.patients = [
      {
        mrn: "5555551212",
        name: "Sam",
        prev_action: "N/A",
        last_action: "Neurosurgeon",
        last_action_date: "N/A",
        appt_date: "Apr 19, 2022",
        todo: "UPDATE APPT"
      },
      {
        mrn: "46355553",
        name: "Nate Patient",
        prev_action: "Scheduled for clinic",
        last_action: "Injections",
        last_action_date: "Apr 5, 2022",
        appt_date: "Apr 8, 2022",
        todo: "UPDATE APPT"
      }
    ];
  }

  apptFilter(event) {
    if (this.patients != undefined || this.patients.length > 0) {
        this.appt_filter = event.target.value;
        if (event.target.value == 'today') {
            this.tableData();
        } else if (event.target.value == 'last ten') {
            this.tableData();
        } else if (event.target.value == 'next ten') {
            this.tableData();
        } else if (event.target.value == 'none') {
            this.tableData();
        } else if (event.target.value == 'all time') {
            this.tableData();
        }
    }
  }

  showDoneItems(event) {
    if (this.patients != undefined) {
        if (event.checked == true) {
            this.show_doneItems = true
            this.tableData();
        }
        else {
            this.show_doneItems = false
            this.tableData();
        }
    }
  }

  showArchived(event) {
    if (this.patients != undefined) {
        if (event.checked == true) {
            this.show_Archived = true
            this.tableData();
        }
        else {
            this.show_Archived = false
            this.tableData();
        }
    }
  }

  showPatientName(event){
    if (event.checked == true){
      this.patientNameShown = false;
    }
    else if(event.checked == false){
      this.patientNameShown = true;
    }
  }

  openUpdateApptDialog(content) {
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {

    }, (reason) => {

    });
  }

  updateAppointment(){

  }

  dismissDialog(){
    this.modalService.dismissAll();
  }
}