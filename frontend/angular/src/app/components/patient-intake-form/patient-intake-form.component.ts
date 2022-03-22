import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
@Component({
    selector: 'app-patient-intake-form',
    templateUrl: './patient-intake-form.component.html',
    styleUrls: ['./patient-intake-form.component.scss']
})
export class PatientIntakeFormComponent implements OnInit {
    name = ' Elia'
    mrn = '32325'
    spineSurgery: any
    smoker: any
    mri_status: any
    lower_back: any
    left_leg: any
    right_leg: any
    back_lower: any
    leg: any
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
        this.referral_reason.forEach(y => {
            if (y.id == id) {
                y.show = !show
            }
        })
    }
    onSelectChange(value, name) {
        console.log('Value', value, name)
    }
    savePatient() {
        console.log('save')
    }
}
