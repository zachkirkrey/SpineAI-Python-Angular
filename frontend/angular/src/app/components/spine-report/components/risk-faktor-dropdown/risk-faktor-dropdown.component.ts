import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-risk-faktor-dropdown',
  templateUrl: './risk-faktor-dropdown.component.html',
  styleUrls: ['../../spine-report.component.scss', './risk-faktor-dropdown.component.scss']
})
export class RiskFaktorDropdownComponent implements OnInit {

  @Input() data: any = {
    title: "Some title",
    risk: !!Math.round(Math.random()),
    text: "Lorem ipsum, dolor sit amet consectetur adipisicing elit. Neque porro odio tenetur, corrupti ipsa soluta distinctio mollitia labore quis cum officia maxime quae suscipit, dignissimos molestiae nisi itaque praesentium nostrum.",
    advices: [
      "Aim to loose - 10 lbs to reduce BMI < 30"
    ]
  };

  opened = false;

  constructor() { }

  ngOnInit(): void {
  }

}
