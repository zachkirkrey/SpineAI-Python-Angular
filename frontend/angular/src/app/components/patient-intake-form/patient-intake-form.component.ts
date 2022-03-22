import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
@Component({
  selector: 'app-patient-intake-form',
  templateUrl: './patient-intake-form.component.html',
  styleUrls: ['./patient-intake-form.component.scss']
})
export class PatientIntakeFormComponent implements OnInit {

  constructor(private router: Router, private route: ActivatedRoute,) { }

  ngOnInit(): void {
  }
navigate() {
        this.router.navigate(['studies']);
    }

}
