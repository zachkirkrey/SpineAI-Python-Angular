import { Component, OnInit, QueryList, ViewChildren } from '@angular/core';
import { ExportService } from 'src/app/services/export/export.service';
import { environment } from 'src/environments/environment';
import * as moment from 'moment';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { v4 as uuidv4 } from 'uuid';
import { Router, NavigationEnd } from '@angular/router';
import { CookieService } from 'ngx-cookie';


@Component({
    selector: 'app-study-list',
    templateUrl: './study-list.component.html',
    styleUrls: ['./study-list.component.scss'],
})
export class StudyListComponent implements OnInit {

    readonly api_url = environment.api_url;
    readonly index_url = `${environment.api_url}/studies?count=1000&scope=includeReports`;
    readonly action_save_url = `${environment.api_url}/action`;
    readonly action_fetch_url = `${environment.api_url}/action`;
    readonly patient_save_url = `${environment.api_url}/studies`;

    old_index = 0
    index = [];
    index_complete = false;
    index_error: string;
    action_error: string;
    section: string = '';
    visibility: Boolean = true;
    action = []
    report_action = []
    action_index = []
    dep = []
    new_index: any;
    closeResult = '';
    name: any;
    mrn: any;
    email: any;
    date_picker: any;
    date_placeholder: string = "Appointment Date"
    appt_date: any
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
    token: any;
    del_action_id: any
    showList: boolean = false
    action_arr = []
    columnValue: any
    isShown: boolean = true
    colShow: boolean = false
    createdCheckbox: any
    importCheckBox: any
    mrnCheckbox: any
    statusCheckbox: any
    aptCheckBox: any
    nameCheckBox: any
    reportCheckBox: any
    recommnCheckBox: any
    actionCheckBox: any
    del_study_id: any
    table_order = 'desc'
    table_name = 'patient_name'
    actionList = ['Scheduled for Clinic', 'Surgery', 'Additional Testing', 'Injections', 'Physical Therapy', 'RTC/DC', 'Referral']
    columnList = [{
        id: 'mrn_col',
        name: 'mrnCheckbox',
        show: true,
        colName: 'MRN # '
    }, {
        id: 'status_col',
        name: 'statusCheckbox',
        show: false,
        colName: 'Status'
    }, {
        id: 'apt_col',
        name: 'aptCheckbox',
        show: true,
        colName: 'APPT DATE'
    }, {
        id: 'created_col',
        name: 'createdCheckbox',
        show: false,
        colName: 'CREATED DATE'
    }, {
        id: 'name_col',
        name: 'nameCheckbox',
        show: true,
        colName: 'PATIENT NAME'
    }, {
        id: 'import_col',
        name: 'importCheckBox',
        show: false,
        colName: 'IMPORT ID'
    }, {
        id: 'report_col',
        name: 'reportCheckbox',
        show: true,
        colName: 'REPORT'
    }, {
        id: 'recommn_col',
        name: 'recommnCheckbox',
        show: true,
        colName: 'RECOMMENDATION'
    }, {
        id: 'action_col',
        name: 'actionCheckbox',
        show: true,
        colName: 'ACTION'
    }]
    @ViewChildren('report_rows') report_rows: QueryList<any>;
    constructor(private exportService: ExportService, private modalService: NgbModal, private router: Router, private cookie: CookieService) {
        this.token = localStorage.getItem('token')
    }
    ngOnInit() {
        this.token = localStorage.getItem('token')
        this.section = 'Hide patient name';
        this.tableData(null);
        this.createdCheckbox = false
        this.importCheckBox = false
        this.mrnCheckbox = true
        this.statusCheckbox = false
        this.aptCheckBox = true
        this.nameCheckBox = true
        this.reportCheckBox = true
        this.recommnCheckBox = true
        this.actionCheckBox = true
        let columnArr = this.cookie.get('columnList')
        let createdCheckbox = this.cookie.get('created_col')
        let importCheckBox = this.cookie.get('import_col')
        let mrnCheckbox = this.cookie.get('mrn_col')
        let statusCheckbox = this.cookie.get('status_col')
        let aptCheckBox = this.cookie.get('apt_col')
        let nameCheckBox = this.cookie.get('name_col')
        let reportCheckBox = this.cookie.get('report_col')
        let recommnCheckBox = this.cookie.get('recommn_col')
        let actionCheckBox = this.cookie.get('action_col')
        if (columnArr != undefined) {
            this.columnList = JSON.parse(columnArr)
        } if (createdCheckbox != undefined) {
            this.createdCheckbox = createdCheckbox
        } if (importCheckBox != undefined) {
            this.importCheckBox = importCheckBox
        } if (statusCheckbox != undefined) {
            this.statusCheckbox = statusCheckbox
        }
        if (mrnCheckbox != undefined) {
            this.mrnCheckbox = mrnCheckbox
        } if (aptCheckBox != undefined) {
            this.aptCheckBox = aptCheckBox
        } if (nameCheckBox != undefined) {
            this.nameCheckBox = nameCheckBox
        } if (reportCheckBox != undefined) {
            this.reportCheckBox = reportCheckBox
        } if (recommnCheckBox != undefined) {
            this.recommnCheckBox = recommnCheckBox
        } if (actionCheckBox != undefined) {
            this.actionCheckBox = actionCheckBox
        }
    }
    checkPlaceHolder() {
        if (this.date_placeholder) {
            this.date_placeholder = null
            return;
        } else {
            this.date_placeholder = 'Appointment Date'
            return
        }
    }
    hide_show_table(col_name, value, index) {
        this.columnList.forEach((x, i) => {
            if (index == i) {
                x.show = !value
            }
        })
        this.cookie.put('columnList', JSON.stringify(this.columnList))
        if (value == false) {
            var all_col = document.getElementsByClassName(col_name);
            for (var i = 0; i < all_col.length; i++) {
                (all_col[i] as HTMLElement).style.display = "table-cell";
            }
            document.getElementById(col_name + "_head").style.display = "table-cell";
        }
        else {
            var all_col = document.getElementsByClassName(col_name);
            for (var i = 0; i < all_col.length; i++) {
                (all_col[i] as HTMLElement).style.display = "none";
            }
            document.getElementById(col_name + "_head").style.display = "none";
        }
        if (col_name == 'mrn_col') {
            this.mrnCheckbox = !value
            this.cookie.put('mrn_col', this.mrnCheckbox)
        }

        if (col_name == 'status_col') {
            this.statusCheckbox = !value
            this.cookie.put('status_col', this.statusCheckbox)
        }
        if (col_name == 'apt_col') {
            this.aptCheckBox = !value
            this.cookie.put('apt_col', this.aptCheckBox)
        } if (col_name == 'created_col') {
            this.createdCheckbox = !value
            this.cookie.put('created_col', this.createdCheckbox)
        }
        if (col_name == 'name_col') {
            this.nameCheckBox = !value
            this.cookie.put('apt_col', this.aptCheckBox)
        }
        if (col_name == 'import_col') {
            this.importCheckBox = !value
            this.cookie.put('import_col', this.importCheckBox)
        }
        if (col_name == 'report_col') {
            this.reportCheckBox = !value
            this.cookie.put('report_col', this.reportCheckBox)
        }
        if (col_name == 'recommn_col') {
            this.recommnCheckBox = !value
            this.cookie.put('recommn_col', this.recommnCheckBox)
        }
        if (col_name == 'action_col') {
            this.actionCheckBox = !value
            this.cookie.put('action_col', this.actionCheckBox)
        }
    }

    colDropdown(value) {
        this.colShow = !value
    }
    searchPacsNavigate(uuid) {
        this.router.navigate(['/fetch/' + uuid]);
    }
    importMRINavigate(uuid, id) {
        this.router.navigate(['/intake/' + uuid + '/' + id])
    }
    tableData(study_id) {
        function sort_by_creation(x, y) {
            return -1;
            if (x.creation_datetime > y.creation_datetime) {
            }
            if (x.creation_datetime < y.creation_datetime) {
                return 1;
            }
            return 0;
        }
        // TODO(billy): Create a dev config for this url so this can work during
        // development.
        $.ajax({
            url: this.index_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            if ('error' in data) {
                this.index_error = data['error'];
            } else {
                this.index = data;
                this.index.forEach((x, i) => {
                    x.show_icon = true
                    x.creation_datetime = moment(x.creation_datetime).format('YYYY-MM-DD')
                    if (study_id != null && study_id == x.id) {
                        x.showList = true
                    }
                    else {
                        x.showList = false
                    }

                    if (x.appointment_date != null) {
                        x.appointment_date = moment(x.appointment_date).format('YYYY-MM-DD')
                    }
                });
                data.forEach(element => {
                    element.Reports = element.Reports.filter(report => report.type == 'PDF_SIMPLE');
                    element.Reports.sort(sort_by_creation);
                });
                this.fetchAction()
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${this.index_url}.`;
        }.bind(this)).always(() => {
            this.index_complete = true;
        });
        this.action_arr = []
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
    createPatient() {
        if (this.email_validate == false) {
            this.email_error = true
        } else if (this.email_validate == true) {
            this.email_error = false
        }
        if (this.name_validate == false) {
            this.name_error = true
        } else if (this.name_validate == true) {
            this.name_error = false
        }
        if (this.mrn_validate == false) {
            this.mrn_error = true
        } else if (this.mrn_validate == true) {
            this.mrn_error = false
        }
        if (this.diagnosis_validate == false) {
            this.diagnosis_error = true
        } else if (this.diagnosis_validate == true) {
            this.diagnosis_error = false

        }
        if (this.number_validate == false) {
            this.number_error = true
        } else if (this.number_validate == true) {
            this.number_error = false
        }

        if (this.date_picker == '') {
            this.dob_error = true
        }
        else if (this.email_validate == true && this.number_validate == true) {
            this.savePatient()

        }
    }
    savePatient() {
        let formatted_time = moment(new Date()).format("YYYY-MM-DD HH:mm:ss");
        let req_data = {
            "uuid": uuidv4(),
            "creation_datetime": formatted_time,
            "name": this.name,
            "file_dir_path": '',
            "file_dir_checksum": '',
            "image_file_type": '',
            "accession_number": '',
            "patient_age": '',
            "patient_name": this.name,
            "patient_size": '',
            "patient_sex": '',
            "study_instance_uid": '',
            "mrn": this.mrn,
            "email": this.email,
            "date_of_birth": this.date_picker,
            "phone_number": this.telephone,
            "diagnosis": this.diagnosis,
            "appointment_date": this.appt_date
        }
        $.ajax({
            url: this.patient_save_url,
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
                this.tableData(null)
                this.fetchAction()
                this.modalService.dismissAll()
                this.name = ''
                this.email = ''
                this.mrn = ''
                this.diagnosis = ''
                this.date_picker = ''
                this.telephone = ''
                this.appt_date = ''

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });
    }
    delModal() {
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
                this.fetchAction()
                this.action = []
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${delete_url}.`;
        }.bind(this)).always(() => {
        });
        this.tableData(this.del_study_id)
        this.modalService.dismissAll()
    }
    closeModal() {
        this.modalService.dismissAll()
        this.name = ''
        this.email = ''
        this.mrn = ''
        this.diagnosis = ''
        this.date_picker = ''
        this.telephone = ''
        this.appt_date = ''
        this.email_error = false
        this.number_error = false
        this.dob_error = false
    }
    open(content) {
        //this.date_picker = new Date()
        this.date_picker = new Date('1/1/1970')
        this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
            this.closeResult = `Closed with: ${result}`;
        }, (reason) => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
        });
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
    fetchAction() {
        $.ajax({
            url: this.action_fetch_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            type: "GET",
        }).done(function (data) {
            if ('error' in data) {
            } else {
                let fetchArr = []
                let filter_arr = []
                if (data && data.length > 0) {
                    data.map(x => {
                        fetchArr.push({
                            'time': moment(x.creation_datetime).format("MM/DD/YY hh:mm a"),
                            'name': x.name,
                            'study': x.study,
                            'id': x.id
                        })
                    })
                    this.index.map(x => {
                        let object = {
                            'study': x.id
                        }
                        filter_arr.push(this.filterArr(fetchArr, object))
                    })

                    filter_arr.map((y, i) => {
                        this.index.forEach(x => {
                            if ((y[0] != undefined && y[0].study) == x.id) {
                                x.report_action = y
                            }
                        });
                    })
                }
                if (this.table_order == 'desc') {
                    if (this.table_name == 'patient_name') {
                        this.index.sort(function (a, b) { return (a.patient_name > b.patient_name) ? 1 : ((b.patient_name > a.patient_name) ? -1 : 0); });
                    } else if (this.table_name == 'mrn') {
                        this.index.sort(function (a, b) { return (a.mrn > b.mrn) ? 1 : ((b.mrn > a.mrn) ? -1 : 0); });
                    } else if (this.table_name == 'appt') {
                        this.index.sort(function (a, b) { return (a.appointment_date > b.appointment_date) ? 1 : ((b.appointment_date > a.appointment_date) ? -1 : 0); });
                    } else if (this.table_name == 'created_date') {
                        this.index.sort(function (a, b) { return (a.creation_datetime > b.creation_datetime) ? 1 : ((b.creation_datetime > a.creation_datetime) ? -1 : 0); });
                    } else if (this.table_name == 'import_id') {
                        this.index.sort(function (a, b) { return (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0); });
                    }

                } else if (this.table_order == 'asc') {
                    if (this.table_name == 'patient_name') {
                        this.index.sort(function (a, b) { return (a.patient_name < b.patient_name) ? 1 : ((b.patient_name < a.patient_name) ? -1 : 0); });
                    } else if (this.table_name == 'mrn') {
                        this.index.sort(function (a, b) { return (a.mrn < b.mrn) ? 1 : ((b.mrn < a.mrn) ? -1 : 0); });
                    } else if (this.table_name == 'appt') {
                        this.index.sort(function (a, b) { return (a.appointment_date < b.appointment_date) ? 1 : ((b.appointment_date < a.appointment_date) ? -1 : 0); });
                    } else if (this.table_name == 'created_date') {
                        this.index.sort(function (a, b) { return (a.creation_datetime < b.creation_datetime) ? 1 : ((b.creation_datetime < a.creation_datetime) ? -1 : 0); });
                    } else if (this.table_name == 'import_id') {
                        this.index.sort(function (a, b) { return (a.name < b.name) ? 1 : ((b.name < a.name) ? -1 : 0); });
                    }
                }

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.action_fetch_url}.`;
        }.bind(this)).always(() => {
        });
        this.action_arr = []
    }

    showViewer(id, data) {
        window.open(
            `${this.api_url}/reports?as=HTML&type=HTML_VIEWER&sort=-creation_datetime&Studies.uuid=${id}&${this.token}`, "_blank")
    }

    filterArr(arr, criteria) {
        return arr.filter(function (obj) {
            return Object.keys(criteria).every(function (c) {
                return obj[c] == criteria[c];
            });
        });
    }
    saveAction(id, index) {
        localStorage.setItem('patient_order', JSON.stringify(this.index))
        let report_Arr = []
        report_Arr = this.action_arr
        report_Arr.forEach(element => {
            this.callSaveAPI(element.name, element.time, id, index)
        });

    }
    deleteAction(id, content, study_id) {
        this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
            this.closeResult = `Closed with: ${result}`;
        }, (reason) => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
        });
        this.del_action_id = id
        this.del_study_id = study_id

    }
    closeDelModal() {
        this.modalService.dismissAll()
    }
    callSaveAPI(name, time, study_id, index) {
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
                    this.index.forEach((x, i) => {
                        if (index == i) {
                            x.show_icon = true
                        }
                        else {
                            x.show_icon = true
                        }

                    });
                }

                this.fetchAction()
                this.action = []

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });
        this.tableData(study_id)
        this.action_arr = []
    }
    showHide(id, showIndex, showList) {
        this.index.forEach((x, i) => {
            if (showIndex == i) {
                x.showList = !x.showList
            }
        });
    }
    actionValues(value, index) {
        const object = {
            'time': moment(new Date()).format("MM/DD/YY hh:mm a"),
            'name': value
        }
        this.action_arr.push(object)
        this.index.forEach((x, i) => {
            if (i == index) {
                x.show_icon = false
            }
        })
        this.new_index = index
        if (this.new_index === this.old_index) {
            const obj = {
                'time': moment(new Date()).format("MM/DD/YY hh:mm a"),
                'name': value
            }
            this.dep.push(obj);
            this.old_index = this.new_index
            this.report_action[index] = this.dep
        } else {
            this.dep = []
            const obj = {
                'time': moment(new Date()).format("MM/DD/YY hh:mm a"),
                'name': value
            }
            this.dep.push(obj);
            this.report_action[index] = this.dep
            this.old_index = this.new_index
        }
    }

    toggleDisplay(event) {
        if (event.checked == true) {
            this.isShown = false;
            this.section = 'Show patient name';
        } else if (event.checked == false) {
            this.isShown = true;
            this.section = 'Hide patient name';
        }
    }
    sortOrder(name) {
        let table = $('#reports_table').DataTable();
        this.table_order = table.order()[0][1]
        this.table_name = name
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
                            $(elem).html('None');
                        } else {
                            if (data[0].surgery_recommended) {
                                $(elem).html('<span style="color: red;">Schedule Consult</span>');
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

    public exportCSV() {
        let csvContent = this.exportService.getCsvExport(this.index);
        let encodedUri = encodeURI(csvContent);
        let link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'spineai_export.csv');
        document.body.appendChild(link);
        link.click();
    }
    navigateToPatient(uuid) {
        this.router.navigate(['/patient/' + uuid])
    }
    redirect(value, uuid, id) {
        if (value == 'intake') {
            this.router.navigate(['/detais/form/' + uuid + '/' + id])
        }
    }
}
