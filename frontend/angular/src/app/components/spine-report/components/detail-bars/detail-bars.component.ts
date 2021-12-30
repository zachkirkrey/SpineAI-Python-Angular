import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ReversePipe } from 'ngx-pipes';

interface Bar {
  intensity: string;
  value: number;
  narrowing: number;
}

@Component({
  selector: 'app-detail-bars',
  templateUrl: './detail-bars.component.html',
  styleUrls: ['../../spine-report.component.scss', './detail-bars.component.scss']
})
export class DetailBarsComponent implements OnInit {

  @Input() index: number = 0;
  @Input() values = [];
  @Input() narrowing = [];
  @Input() reverse = false;

  @Output() indexChanged = new EventEmitter<number>(true);

  threshold: number = 0.2;
  visualIndex: number;
  max_value = 0;
  bars = new Array<Bar>();

  constructor() { }

  ngOnInit(): void {
    this.values.forEach((value) => {
      if (value > this.max_value) this.max_value = value;
    });

    for (let i = 0; i < this.values.length; i++) {
      let value = this.values[i];
      let narrowing = this.narrowing[i];

      let intensity = '';
      if (narrowing > this.threshold) {
        intensity = 'severe';
      } else if (narrowing > this.threshold * 0.75) {
        intensity = 'moderate';
      }

      this.bars.push({
        value: Math.round(value * 100) / 100,
        narrowing: Math.round(narrowing * 100),
        intensity: intensity
      });
    }

    if (this.reverse) {
      this.bars.reverse();
    }
  }

  ngOnChanges(changes): void {
    if (changes['index']) {
      let newVisualIndex = this.index;
      if (this.reverse) {
        newVisualIndex = this.values.length - 1 - this.index;
      }
      if (this.visualIndex != newVisualIndex) {
        this.visualIndex = newVisualIndex;
      }
    }
  }

  ngOnDestroy(): void {
    this.indexChanged.unsubscribe();
  }

  changed(newVisualIndex) {
    let index = this.visualIndex;
    if (this.reverse) {
      index = this.values.length - 1 - this.visualIndex;
    }
    this.indexChanged.emit(index);
  }
}
