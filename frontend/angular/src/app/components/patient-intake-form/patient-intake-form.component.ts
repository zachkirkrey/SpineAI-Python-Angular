import { Component, OnInit, ViewChild, TemplateRef } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { environment } from 'src/environments/environment';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import * as moment from 'moment';
@Component({
    selector: 'app-patient-intake-form',
    templateUrl: './patient-intake-form.component.html',
    styleUrls: ['./patient-intake-form.component.scss']
})
export class PatientIntakeFormComponent implements OnInit {
    spineSurgery: any
    smoker: any
    mri_status: any
    lower_back: any
    left_leg: any
    right_leg: any
    back_lower: any
    leg: any
    study_id: any
    token: any
    study_uuid: any
    intake_form = []
    otherQues = []
    patient_name: any
    mrn: any
    closeResult = '';
    referral_reason = []
    symptoms_arr = []
    patient_save: boolean = false
    prev_spine = [{ 'id': 1, 'name': 'Yes', 'value': true }, { 'id': 2, 'name': 'No', 'value': false }]
    otherTreat_arr = []
    history_arr = []
    smoker_arr = [{ 'id': 1, 'name': 'Yes', 'value': true }, { 'id': 2, 'name': 'No', 'value': false }]
    mri_arr = [{ 'id': 1, 'name': 'Upload Link Sent', 'show': false }, { 'id': 2, 'name': 'Mailing In', 'show': false }, { 'id': 3, 'name': 'In System', 'show': false }]
    pain_arr = [{ 'id': 1, 'name': 'Lower Back', 'show': false }, { 'id': 2, 'name': 'Left Leg', 'show': false }, { 'id': 3, 'name': 'Right Leg', 'show': false }, { 'id': 4, 'name': '% Lower Back', 'show': false }, { 'id': 5, 'name': '% Leg', 'show': false }]
    number_arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    showMsg: any
    updation_datetime: any
    unamePattern = "(100)|(0*\d{1,2})";
    lower_back_ValidateMsg: any
    leg_validation: any
    @ViewChild('msgModal') msgModal: TemplateRef<any>;
    constructor(private router: Router, private route: ActivatedRoute, private modalService: NgbModal) {
        this.study_id = this.route.snapshot.params.id
        this.study_uuid = this.route.snapshot.params.uuid
    }
    ngOnInit(): void {
        this.updation_datetime = moment(new Date()).format('MM/DD/YYYY')
        this.getReferralReason()
        this.getSymptoms()
        this.getTreatments()
        this.getHistory()
        this.fetchQuestions()
        this.token = localStorage.getItem('token')


    }
    navigate() {
        this.router.navigate(['studies']);
    }
    onItemChange(event, id, show, name) {
        if (name == 'history') {
            this.history_arr.map(x => {
                if (x.id == id) {
                    x.show = !show
                }
            })
            this.history_arr.map(x => {
                if (x.show == true) {
                    this.saveHistory(x.id)
                }
            })
        }
        else if (name == 'refReason') {
            this.referral_reason.map(x => {
                if (x.id == id) {
                    x.show = !show
                }
            })
            this.referral_reason.map(x => {
                if (x.show == true) {
                    this.saveRefReason(x.id)
                }
            })
        }
        else if (name == 'otherTreatment') {
            this.otherTreat_arr.map(x => {
                if (x.id == id) {
                    x.show = !show
                }
            })
            this.otherTreat_arr.map(x => {
                if (x.show == true) {
                    this.saveOthrTreat(x.id)
                }
            })
        }
        else if (name == 'symptoms') {
            this.symptoms_arr.map(x => {
                if (x.id == id) {
                    x.show = !show
                }
            })
            this.symptoms_arr.map(x => {
                if (x.show == true) {
                    this.saveSymptoms(x.id)
                }
            })
        }


    }
    onSelectChange(value, name) {
        console.log('Value', value, name)
    }
    saveHistory(id) {
        let history_save_url = `${environment.api_url}/save/history`;
        let req_data = {
            'history': id,
            'study': parseInt(this.study_id)
        }
        $.ajax({
            url: history_save_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,

        }).done(function (data) {
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${history_save_url}.`;
        }.bind(this)).always(() => {
        });
    }
    saveRefReason(id) {
        let ref_save_url = `${environment.api_url}/save/ReferralReason`;
        let req_data = {
            'referralreason': id,
            'study': parseInt(this.study_id)
        }
        $.ajax({
            url: ref_save_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,

        }).done(function (data) {
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${ref_save_url}.`;
        }.bind(this)).always(() => {
        });
    }
    saveOthrTreat(id) {
        let treat_save_url = `${environment.api_url}/save/OtherTreatments`;
        let req_data = {
            'othertreatment': id,
            'study': parseInt(this.study_id)
        }
        $.ajax({
            url: treat_save_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,

        }).done(function (data) {

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${treat_save_url}.`;
        }.bind(this)).always(() => {
        });
    }
    saveSymptoms(id) {
        let symptoms_save_url = `${environment.api_url}/save/symptoms`;
        let req_data = {
            'symptoms': id,
            'study': parseInt(this.study_id)
        }
        $.ajax({
            url: symptoms_save_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,

        }).done(function (data) {

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${symptoms_save_url}.`;
        }.bind(this)).always(() => {
        });
    }
    getReferralReason() {
        let referral_url = `${environment.api_url}/referralreasons`;
        $.ajax({
            url: referral_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.referral_reason = data
            this.referral_reason.forEach(y => {
                y.show = false

            })
            this.fetchRef()
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${referral_url}.`;
        }.bind(this)).always(() => {
        });

    }
    getSymptoms() {
        let symptoms_url = `${environment.api_url}/symptoms`;
        $.ajax({
            url: symptoms_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.symptoms_arr = data
            this.symptoms_arr.forEach(y => {
                y.show = false

            })
            this.fetchSymptoms()
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${symptoms_url}.`;
        }.bind(this)).always(() => {
        });
    }
    getTreatments() {
        let treatments_url = `${environment.api_url}/treatments`;
        $.ajax({
            url: treatments_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.otherTreat_arr = data
            this.otherTreat_arr.forEach(y => {
                y.show = false

            })
            this.fetchOthrTreat()

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${treatments_url}.`;
        }.bind(this)).always(() => {
        });
    }
    getHistory() {
        let history_url = `${environment.api_url}/history`;
        $.ajax({
            url: history_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.history_arr = data
            this.history_arr.forEach(y => {
                y.show = false

            })
            this.fetchHistory()
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${history_url}.`;
        }.bind(this)).always(() => {
        });

    }
    fetchQuestions() {
        let question_url = `${environment.api_url}/study/${this.study_uuid}?scope=includeQuestions`;
        $.ajax({
            url: question_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.intake_form = data
            this.patient_name = this.intake_form.patient_name
            this.mrn = this.intake_form.mrn
            if (this.intake_form.OtherQuestions.length > 0) {

                this.otherQues = this.intake_form.OtherQuestions
                this.lower_back = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].lower_back
                this.left_leg = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].left_leg
                this.right_leg = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].right_leg
                this.back_lower = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].percent_lower_back
                this.leg = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].percent_leg
                this.spineSurgery = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].previous_spine_surgery
                this.smoker = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].current_smoker
                this.mri_status = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].mri_status
                this.study_id = this.intake_form.OtherQuestions.length > 0 && this.intake_form.OtherQuestions[0].study
                this.updation_datetime = this.intake_form.OtherQuestions.length > 0 && moment(this.intake_form.OtherQuestions[0].updation_datetime).format('MM/DD/YYYY')
            }

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${question_url}.`;
        }.bind(this)).always(() => {
        });
    }
    fetchHistory() {
        let history_url = `${environment.api_url}/study/${this.study_uuid}?scope=includeHistory`;
        $.ajax({
            url: history_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            let result = data
            if (result.Histories.length > 0) {
                this.history_arr.map(x => {
                    return result.Histories.map(y => {
                        if (y.id == x.id) {
                            x.show = true
                        }
                    })
                })
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${history_url}.`;
        }.bind(this)).always(() => {
        });
    }
    fetchOthrTreat() {
        let treat_url = `${environment.api_url}/study/${this.study_uuid}?scope=includeOtherTreatments`;
        $.ajax({
            url: treat_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            let result = data
            if (result.OtherTreatments.length > 0) {
                this.otherTreat_arr.map(x => {
                    return result.OtherTreatments.map(y => {
                        if (y.id == x.id) {
                            x.show = true
                        }
                    })
                })
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${treat_url}.`;
        }.bind(this)).always(() => {
        });
    }
    fetchSymptoms() {
        let symptoms_url = `${environment.api_url}/study/${this.study_uuid}?scope=includeSymptoms`;
        $.ajax({
            url: symptoms_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            let result = data
            if (result.Symptoms.length > 0) {
                this.symptoms_arr.map(x => {
                    return result.Symptoms.map(y => {
                        if (y.id == x.id) {
                            x.show = true
                        }
                    })
                })
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${symptoms_url}.`;
        }.bind(this)).always(() => {
        });
    }
    fetchRef() {
        let ref_url = `${environment.api_url}/study/${this.study_uuid}?scope=includeReferralReason`;
        $.ajax({
            url: ref_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            let result = data
            if (result.ReferralReasons.length > 0) {
                this.referral_reason.map(x => {
                    return result.ReferralReasons.map(y => {
                        if (y.id == x.id) {
                            x.show = true
                        }
                    })
                })
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${ref_url}.`;
        }.bind(this)).always(() => {
        });
    }
    updateOuestions() {
        let update_url = `${environment.api_url}/question/${this.study_uuid}`;
        let formatted_time = moment(new Date()).format("YYYY-MM-DD HH:mm:ss");
        let req_data = {
            "lower_back": this.lower_back,
            "left_leg": this.left_leg,
            "right_leg": this.right_leg,
            "percent_lower_back": this.back_lower,
            "percent_leg": this.leg,
            "previous_spine_surgery": this.spineSurgery,
            "current_smoker": this.smoker,
            "mri_status": this.mri_status,
            "study": this.study_id,
            'uuid': this.study_uuid,
            'id': this.study_id,
            'updation_datetime': formatted_time
        }
        $.ajax({
            url: update_url,
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
    saveQuestions() {
        let question_url = `${environment.api_url}/questions`;
        let formatted_time = moment(new Date()).format("YYYY-MM-DD HH:mm:ss");
        let req_data = {
            "lower_back": this.lower_back,
            "left_leg": this.left_leg,
            "right_leg": this.right_leg,
            "percent_lower_back": this.back_lower,
            "percent_leg": this.leg,
            "previous_spine_surgery": this.spineSurgery,
            "current_smoker": this.smoker,
            "mri_status": this.mri_status,
            "study": this.study_id,
            'uuid': this.study_uuid,
            'id': this.study_id,
            'updation_datetime': formatted_time
        }
        $.ajax({
            url: question_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,
        }).done(function (data) {
            if ('error' in data) { } else {
                this.patient_save = true
                this.open(this.msgModal)
                this.showMsg = 'Patient information saved successfully !!'
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${question_url}.`;
        }.bind(this)).always(() => {
        });
    }
    closeDelModal() {
        this.modalService.dismissAll()
    }
    open(content) {
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
    savePatient(content) {
        let referralArr = this.referral_reason.filter(x => {
            return x.show == true
        })
        let symptoms = this.symptoms_arr.filter(x => {
            return x.show == true
        })
        let otherTreatArr = this.otherTreat_arr.filter(x => {
            return x.show == true
        })
        let historyArr = this.history_arr.filter(x => {
            return x.show == true
        })
        console.log('save', referralArr, this.lower_back, this.left_leg, this.right_leg, this.back_lower, this.leg, symptoms, this.spineSurgery, otherTreatArr, historyArr, this.smoker, this.mri_status)
        if (referralArr.length == 0 || symptoms.length == 0 || otherTreatArr.length == 0 || historyArr.length == 0 || this.lower_back == undefined || this.left_leg == undefined || this.right_leg == undefined || this.back_lower == undefined || this.leg == undefined || this.spineSurgery == undefined || this.smoker == undefined || this.mri_status == undefined) {
            this.open(content)
            this.showMsg = 'Please fill all the fields !!'
        }
        else if (this.otherQues.length > 0 || this.patient_save == true) {
            this.updateOuestions()
        }
        else {
            this.saveQuestions()
        }

    }
    keyPress(value, e, name) {
        if (name == 'back_lower') {
            if (parseInt(value) < 1 || parseInt(value) > 100) {
                console.log("Value should be between 0 - 100");
                this.lower_back_ValidateMsg = 'Value should be between 1 - 100'
                return;
            } else {
                this.lower_back_ValidateMsg = ''
            }
        }
        else if (name == 'leg') {
            if (parseInt(value) < 100) {
                console.log("Value should be between 0 - 100");
                this.leg_validation = 'Value should be above 100'
                return;
            } else {
                this.leg_validation = ''
            }
        }
    }
}
