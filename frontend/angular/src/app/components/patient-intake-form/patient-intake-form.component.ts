import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
@Component({
    selector: 'app-patient-intake-form',
    templateUrl: './patient-intake-form.component.html',
    styleUrls: ['./patient-intake-form.component.scss']
})
export class PatientIntakeFormComponent implements OnInit {
    name = 'Elia'
    mrn = '32325'
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
    referral_reason = [{ 'id': 1, 'name': 'Herniated or bulging disc', 'show': false }, { 'id': 2, 'name': 'Arthritis or degenerative changes', 'show': false }, { 'id': 3, 'name': 'Spondylolisthesis', 'show': false }, { 'id': 4, 'name': 'Fracture', 'show': false }]
    symptoms_arr = [{ 'id': 1, 'name': 'Bowel or bladder dysfunction', 'show': false }, { 'id': 2, 'name': 'Saddle anesthesia', 'show': false }, { 'id': 3, 'name': 'Rapidly progressing weakness', 'show': false }]
    prev_spine = [{ 'id': 1, 'name': 'Yes' }, { 'id': 2, 'name': 'No' }]
    otherTreat_arr = [{ 'id': 1, 'name': 'Physical Therapy', 'show': false }, { 'id': 2, 'name': 'Steroidal Injections', 'show': false }, { 'id': 3, 'name': 'Ablation Therapy', 'show': false }]
    history_arr = [{ 'id': 1, 'name': 'Cardiovascular Disease', 'show': false }, { 'id': 2, 'name': 'Pulmonary Disease', 'show': false }, { 'id': 3, 'name': 'Cancer', 'show': false }, { 'id': 4, 'name': 'Rheumatologic disorders', 'show': false }, { 'id': 5, 'name': 'Endocrine', 'show': false }]
    smoker_arr = [{ 'id': 1, 'name': 'Yes' }, { 'id': 2, 'name': 'No' }]
    mri_arr = [{ 'id': 1, 'name': 'Upload Link Sent', 'show': false }, { 'id': 2, 'name': 'Mailing In', 'show': false }, { 'id': 3, 'name': 'In System', 'show': false }]
    pain_arr = [{ 'id': 1, 'name': 'Lower Back', 'show': false }, { 'id': 2, 'name': 'Left Leg', 'show': false }, { 'id': 3, 'name': 'Right Leg', 'show': false }, { 'id': 4, 'name': '% Lower Back', 'show': false }, { 'id': 5, 'name': '% Leg', 'show': false }]
    number_arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    constructor(private router: Router, private route: ActivatedRoute,) { }

    ngOnInit(): void {
    }
    navigate() {
        this.router.navigate(['studies']);
    }
    onItemChange(event, id, show) {
        console.log('onItemChange', id, show)
        //this.referral_reason.forEach(y => {
        //    if (y.id == id) {
        //        y.show = !show
        //    }
        //})
    }
    onSelectChange(value, name) {
        console.log('Value', value, name)
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

    }
}
