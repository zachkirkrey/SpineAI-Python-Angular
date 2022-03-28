import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { environment } from 'src/environments/environment';
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
    ref_error: boolean = false
    symptoms_error: boolean = false
    other_error: boolean = false
    history_error: boolean = false
    lower_back_error: boolean = false
    left_leg_error: boolean = false
    right_leg_error: boolean = false
    back_lower_error: boolean = false
    leg_error: boolean = false
    spineSurgery_error: boolean = false
    smoker_error: boolean = false
    mri_status_error: boolean = false
    study_id: any
    token: any
    study_uuid: any
    intake_form = []
    otherQues = []
    patient_name:any
    mrn:any
    referral_reason = [{ 'id': 1, 'name': 'Herniated or bulging disc', 'show': false }, { 'id': 2, 'name': 'Arthritis or degenerative changes', 'show': false }, { 'id': 3, 'name': 'Spondylolisthesis', 'show': false }, { 'id': 4, 'name': 'Fracture', 'show': false }]
    symptoms_arr = [{ 'id': 1, 'name': 'Bowel or bladder dysfunction', 'show': false }, { 'id': 2, 'name': 'Saddle anesthesia', 'show': false }, { 'id': 3, 'name': 'Rapidly progressing weakness', 'show': false }]
    prev_spine = [{ 'id': 1, 'name': 'Yes', 'value': true }, { 'id': 2, 'name': 'No', 'value': false }]
    otherTreat_arr = [{ 'id': 1, 'name': 'Physical Therapy', 'show': false }, { 'id': 2, 'name': 'Steroidal Injections', 'show': false }, { 'id': 3, 'name': 'Ablation Therapy', 'show': false }]
    history_arr = [{ 'id': 1, 'name': 'Cardiovascular Disease', 'show': false }, { 'id': 2, 'name': 'Pulmonary Disease', 'show': false }, { 'id': 3, 'name': 'Cancer', 'show': false }, { 'id': 4, 'name': 'Rheumatologic disorders', 'show': false }, { 'id': 5, 'name': 'Endocrine', 'show': false }]
    smoker_arr = [{ 'id': 1, 'name': 'Yes', 'value': true }, { 'id': 2, 'name': 'No', 'value': false }]
    mri_arr = [{ 'id': 1, 'name': 'Upload Link Sent', 'show': false }, { 'id': 2, 'name': 'Mailing In', 'show': false }, { 'id': 3, 'name': 'In System', 'show': false }]
    pain_arr = [{ 'id': 1, 'name': 'Lower Back', 'show': false }, { 'id': 2, 'name': 'Left Leg', 'show': false }, { 'id': 3, 'name': 'Right Leg', 'show': false }, { 'id': 4, 'name': '% Lower Back', 'show': false }, { 'id': 5, 'name': '% Leg', 'show': false }]
    number_arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    constructor(private router: Router, private route: ActivatedRoute,) {
        this.study_id = this.route.snapshot.params.id
        this.study_uuid = this.route.snapshot.params.uuid
    }
    ngOnInit(): void {
        this.fetchQuestions()
        this.token = localStorage.getItem('token')
        this.getReferralReason()
        this.getSymptoms()
        this.getTreatments()
        this.getHistory()
    }
    navigate() {
        this.router.navigate(['studies']);
    }
    onItemChange(event, id, show) {
        //this.referral_reason.forEach(y => {
        //    if (y.id == id) {
        //        y.show = !show
        //    }
        //})
    }
    onSelectChange(value, name) {
        console.log('Value', value, name)
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
            this.patient_name= this.intake_form.patient_name
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
            }


        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${question_url}.`;
        }.bind(this)).always(() => {
        });
    }
    updateOuestions() {
        let update_url = `${environment.api_url}/question/${this.study_uuid}`;
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
            'id': this.study_id
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
                this.modalService.dismissAll()
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });
    }
    saveOuestions() {
        let question_url = `${environment.api_url}/questions`;
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
            'id': this.study_id
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
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${question_url}.`;
        }.bind(this)).always(() => {
        });
    }
    savePatient() {
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
        if (referralArr.length < 0) {
            this.ref_error = true
        } if (symptoms.length < 0) {
            this.symptoms_error = true
        } if (otherTreatArr.length < 0) {
            this.other_error = true
        } if (historyArr.length < 0) {
            this.history_error = true
        } if (this.lower_back == undefined) {
            this.lower_back_error = true
        }
        if (this.left_leg == undefined) {
            this.left_leg_error = true
        }
        if (this.right_leg == undefined) {
            this.right_leg_error = true
        }
        if (this.back_lower == undefined) {
            this.back_lower_error = true
        }
        if (this.leg == undefined) {
            this.leg_error = true
        }
        if (this.spineSurgery == undefined) {
            this.spineSurgery_error = true
        }
        if (this.smoker == undefined) {
            this.smoker_error = true
        }
        if (this.mri_status == undefined) {
            this.mri_status_error = true
        }
        if (this.otherQues.length > 0) {
            this.updateOuestions()
        } else {
            this.saveOuestions()
        }

    }
}
