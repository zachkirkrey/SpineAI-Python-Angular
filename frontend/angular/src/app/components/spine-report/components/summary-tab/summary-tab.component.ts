import { Component, Input, OnInit } from '@angular/core';

import { ImageUrls } from 'src/app/components/spine-report/components/image-viewer/image-viewer.component';

@Component({
  selector: 'app-summary-tab',
  templateUrl: './summary-tab.component.html',
  styleUrls: ['../../spine-report.component.scss', './summary-tab.component.scss']
})
export class SummaryTabComponent implements OnInit {

  @Input() images: ImageUrls;
  @Input() sagittalImages: ImageUrls;
  @Input() report;

  showSegmentation: boolean = true;
  discLevels: Array<any>;
  midSagittalIndex: number;

  constructor() { }

  getIntensity(report, narrowing): string {
    let threshold = report.measurements.canal_narrowing.narrowing_threshold;
    if (narrowing > threshold) {
      return 'severe';
    } else if (narrowing > threshold * 0.75) {
      return 'moderate';
    }
    return '';
  }

  ngOnInit(): void {
    let canalSegmentation = this.report.canal_segmentation;
    let numSlices = canalSegmentation.all_canal_areas.length;

    // Determine if canal slices are sequenced top to bottom or reversed.
    // If they are, reverse shown slice #s.
    let imagePositions = this.report.canal_segmentation.image_positions;
    let topToBottom = false;
    if (imagePositions[0][2] > imagePositions[imagePositions.length - 1][2]) {
      topToBottom = true;
    }

    this.discLevels = [
      { i: 0, l: "L1/L2" },
      { i: 1, l: "L2/L3" },
      { i: 2, l: "L3/L4" },
      { i: 3, l: "L4/L5" },
      { i: 4, l: "L5/S1" }
    ].map(levels => {
      let index: number = levels.i;
      if (!topToBottom) index = 4 - index;

      let level = levels.l;
      let viewSliceIndex, sliceIndex = canalSegmentation.canal_slices[index];
      if (!topToBottom) viewSliceIndex = numSlices - 1 - sliceIndex;
      let narrowing = this.report.measurements.canal_narrowing.narrowing[sliceIndex];
      return {
        level: level,
        sliceIndex: sliceIndex,
        viewSliceIndex: viewSliceIndex,
        images: <ImageUrls> {
          rawUrls: this.images.rawUrls[sliceIndex],
          segUrls: this.images.segUrls[sliceIndex]
        },
        area: Math.round(canalSegmentation.canal_areas[index] * 100) / 100,
        narrowing: Math.round(narrowing * 100),
        intensity: this.getIntensity(this.report, narrowing)
      }
    });

      this.midSagittalIndex = Math.round(
        (this.sagittalImages.rawUrls.length - 1) / 2);
  }

  setIntensity() {
    const arr = ['', 'moderate', 'severe'];
    const i = Math.round(Math.random() * 2);
    return arr[i];
  }

  get random() {
    return !!Math.round(Math.random());
  }

}
