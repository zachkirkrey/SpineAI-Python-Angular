import { Component, OnInit, QueryList, ViewChildren, ViewChild, TemplateRef } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import * as moment from 'moment';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';

@Component({
    selector: 'app-patient-component',
    templateUrl: './patient-component.component.html',
    styleUrls: ['./patient-component.component.scss']
})
export class PatientComponentComponent implements OnInit {

    name: any;
    mrn: any;
    email: any;
    date_picker: any;
    appt_date: any;
    telephone: any;
    diagnosis: any;
    email_error: boolean = false
    email_validate: boolean = false
    mrn_error: boolean = false
    mrn_validate: boolean = false
    diagnosis_error: boolean = false
    diagnosis_validate: boolean = false
    name_error: boolean = false
    name_validate: boolean = false
    number_validate: boolean = false
    number_error: boolean = false
    save_action: boolean = false
    dob_error: boolean = false
    token: any
    patient_id: any
    recommendation: any
    report: any
    patient_info = []
    metadata: any
    action_arr = []
    old_index = 0
    index = [];
    index_complete = false;
    index_error: string;
    action_error: string;
    section: string = '';
    visibility: Boolean = true;
    action: any
    report_action = []
    action_index = []
    dep = []
    new_index: any;
    show_icon: any;
    showList: any;
    report_actions = []
    fetchArr = []
    closeResult = '';
    del_action_id: any
    showMsg: any
    readonly api_url = environment.api_url;
    readonly index_url = `${environment.api_url}/studies?count=1000&scope=includeReports`;
    readonly action_fetch_url = `${environment.api_url}/action`;
    readonly action_save_url = `${environment.api_url}/action`;
    @ViewChild('msgModal') msgModal: TemplateRef<any>;
    actionList = ['Scheduled for Clinic', 'Surgery', 'Additional Testing', 'Injections', 'Physical Therapy', 'RTC/DC', 'Referral']
    @ViewChildren('report_rows') report_rows: QueryList<any>;
    constructor(private router: Router, private route: ActivatedRoute, private modalService: NgbModal) {
        this.patient_id = this.route.snapshot.params.id
    }

    ngOnInit(): void {
        this.date_picker = new Date()
        this.token = localStorage.getItem('token')
        this.getPatientInfo()
    }
    navigate() {
        this.router.navigate(['studies']);
    }
    getPatientInfo() {
        let patient_url = `${environment.api_url}/study/${this.patient_id}?scope=includeActions`;
        function sort_by_creation(x, y) {
            return -1;
        }
        $.ajax({
            url: this.index_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            if ('error' in data) {
                console.log('error')
            } else {
                this.index = data;
                if (this.index != undefined && this.index.length > 0) {
                    $.ajax({
                        url: patient_url,
                        headers: {
                            "Authorization": 'Bearer ' + this.token
                        },
                        dataType: 'json',
                    }).done(function (data) {
                        let patient_data = []
                        patient_data.push(data)
                        this.callAction(this.patient_id)
                        this.index.map(x => {
                            patient_data.map(y => {
                                if (y.uuid == x.uuid) {
                                    this.patient_info.push(x)
                                }
                            })
                        })
                        let obj = {
                            show_icon: true,
                            showList: false
                        }

                        this.metadata = {
                            ...this.patient_info[0],
                            ...obj

                        }
                        this.name = this.patient_info[0].patient_name
                        this.mrn = this.patient_info[0].mrn
                        this.appt_date = this.patient_info[0].appointment_date == 'Invalid date' ? '' : this.patient_info[0].appointment_date
                        this.email = this.patient_info[0].email
                        this.diagnosis = this.patient_info[0].diagnosis
                        this.telephone = this.patient_info[0].phone_number
                        this.date_picker = this.patient_info[0].date_of_birth
                        this.recommendation = this.patient_info[0].id
                        this.report = this.patient_info[0].Reports
                        this.show_icon = obj.show_icon
                        this.showList = obj.showList
                        console.log('patient_info', this.metadata, ' ', this.showList)
                    }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
                        this.index_error = `Could not fetch search index from ${patient_url}.`;
                    }.bind(this)).always(() => {
                    });
                }

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${this.index_url}.`;
        });
        this.action_arr = []
    }

    callAction(id) {
        let patient_url = `${environment.api_url}/study/${id}?scope=includeActions`;
        $.ajax({
            url: patient_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.fetchArr = data.Actions
            this.fetchArr.map(x => {
                this.report_actions.push({
                    'time': moment(x.creation_datetime).format("MM/DD/YY hh:mm a"),
                    'name': x.name,
                    'study': x.study,
                    'id': x.id
                })
            })
            console.log('data', this.report_actions)

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${patient_url}.`;
        }.bind(this)).always(() => {
        });
    }

    alphabetValidate(value, name) {
        let regex = new RegExp("^[a-zA-Z0-9]*$");
        if (name == 'name') {
            this.name_validate = regex.test(value)
        } else if (name == 'mrn') {
            this.mrn_validate = regex.test(value)
        } else if (name == 'diagnosis') {
            this.diagnosis_validate = regex.test(value)
        }
        if (this.name_validate == false && name == 'name') {
            this.name_error = true
        } else if (this.name_validate == true && name == 'name') {
            this.name_error = false
        }
        if (this.mrn_validate == false && name == 'mrn') {
            this.mrn_error = true
        } else if (this.mrn_validate == true && name == 'mrn') {
            this.mrn_error = false
        }
        if (this.diagnosis_validate == false && name == 'diagnosis') {
            this.diagnosis_error = true
        } else if (this.diagnosis_validate == true && name == 'diagnosis') {
            this.diagnosis_error = false
        }
    }
    numberValidate(value) {
        let regex = new RegExp('^[0-9]+$');
        this.number_validate = regex.test(value)
        if (this.number_validate == false) {
            this.number_error = true
        } else {
            this.number_error = false
        }
    }
    emailValidate(value) {
        let regex = new RegExp('[a-z0-9]+@[a-z]+\.[a-z]{2,3}');
        this.email_validate = regex.test(value)
        if (this.email_validate == false) {
            this.email_error = true
        } else {
            this.email_error = false
        }
    }
    searchPacsNavigate(uuid) {
        this.router.navigate(['/fetch/' + uuid]);
    }
    importMRINavigate(uuid) {
        this.router.navigate(['/intake/' + uuid])
    }
    showViewer(id, data) {
        window.open(
            `${this.api_url}/reports?as=HTML&type=HTML_VIEWER&sort=-creation_datetime&Studies.uuid=${id}&${this.token}`, "_blank")
    }

    actionValues(value) {
        const object = {
            'time': moment(new Date()).format("MM/DD/YY hh:mm a"),
            'name': value
        }
        this.action_arr.push(object)
        this.patient_info
        this.show_icon = false
        console.log('Action_Arr', this.action_arr)
    }
    showHide() {
        this.showList = !this.showList
        console.log('showList', this.showList)
    }
    saveAction(id, index) {
        let report_Arr = []
        report_Arr = this.action_arr
        report_Arr.forEach(element => {
            this.callSaveAPI(element.name, element.time, id, index)
        });

    }
    callSaveAPI(name, time, study_id, index) {
        this.report_actions = []
        let formatted_time = moment(time).format("YYYY-MM-DD HH:mm:ss");
        let req_data = {
            "name": name,
            "creation_datetime": formatted_time,
            "study": parseInt(study_id)
        }
        $.ajax({
            url: this.action_save_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,
        }).done(function (data) {
            if ('error' in data) {
                this.action_error = data['error'];
            } else {
                let obj = data
                if (obj && Object.keys(obj).length != 0 && Object.getPrototypeOf(obj) === Object.prototype) {
                    this.show_icon = true
                }

                this.action = ''

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });

        this.action_arr = []
        this.callAction(this.patient_id)
    }
    deleteAction(id, content) {
        this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
            this.closeResult = `Closed with: ${result}`;
        }, (reason) => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
        });
        this.del_action_id = id

    }
    getDismissReason(reason: any): string {
        if (reason === ModalDismissReasons.ESC) {
            return 'by pressing ESC';
        } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
            return 'by clicking on a backdrop';
        } else {
            return `with: ${reason}`;
        }
    }
    open(content) {
        this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
            this.closeResult = `Closed with: ${result}`;
        }, (reason) => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
        });
    }
    delModal() {
        this.report_actions = []
        let delete_url = `${environment.api_url}/action/${this.del_action_id}`
        $.ajax({
            url: delete_url,
            type: "Delete",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },

        }).done(function (data) {
            if ('error' in data) { }
            else {
                this.action = ''
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${delete_url}.`;
        }.bind(this)).always(() => {
        });
        this.modalService.dismissAll()
        this.callAction(this.patient_id)
    }
    closeDelModal() {
        this.modalService.dismissAll()
    }

    updatePatient() {
        let patient_save_url = `${environment.api_url}/study/${this.patient_id}`;
        let req_data = {
            "patient_name": this.name,
            "mrn": this.mrn,
            "email": this.email,
            "date_of_birth": this.date_picker,
            "phone_number": this.telephone,
            "diagnosis": this.diagnosis,
            "appointment_date": this.appt_date
        }
        $.ajax({
            url: patient_save_url,
            dataType: 'json',
            type: "PUT",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,
        }).done(function (data) {
            if ('error' in data) {
                this.action_error = data['error'];
            } else {
                this.open(this.msgModal)
                this.showMsg = 'Patient Information Updated Successfully !!'
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });
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

        function load_recommendation(token) {

            $('.recommendation_cell').each(function (i, elem) {
                let id = $(elem).data('study-id');
                $.ajax({
                    url: environment.api_url + `/reports?Studies.id=${id}&type=PDF_SIMPLE`,
                    headers: {
                        "Authorization": 'Bearer ' + localStorage.getItem('token')
                    },
                    dataType: 'json',
                })
                    .done(function (data) {
                        if (!data || !data.length) {
                            $(elem).html('Unknown');
                        } else {
                            if (data[0].surgery_recommended) {
                                $(elem).html('<span style="color: red;">Schedule Consultation</span>');
                            } else {
                                $(elem).html('No Consultation');
                            }
                        }
                    });
            });
        }

        this.report_rows.changes.subscribe(t => {
            $('#reports_table').DataTable({
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
                destroy: false
            });
            $('#reports_table').on('draw.dt', load_recommendation);
            load_recommendation(this.token);
        });
    }

}
