import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-spine-risk-score-bar',
  templateUrl: './spine-risk-score-bar.component.html',
  styleUrls: ['../../spine-report.component.scss', './spine-risk-score-bar.component.scss']
})
export class SpineRiskScoreBarComponent implements OnInit {

  @Input() score: number = 2;
  @Input() threshold: number = 6;
  @Input() score_max: number = 10;
  score_percentage = 0;
  threshold_percentage = 0;

  constructor() { }

  ngOnInit(): void {
    if (this.score > this.score_max) {
      this.score = this.score_max;
    }

    // TODO(billy): Support arithmetic errors.
    this.score_percentage = Math.round(this.score/this.score_max * 100);
    this.threshold_percentage = Math.round(this.threshold/this.score_max * 100);
  }

  get position() {
    return `calc(${this.score_percentage}% - 16px)`;
  }

}
