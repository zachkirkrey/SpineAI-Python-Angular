import { Component, Input, OnInit } from '@angular/core';

import { ImageUrls } from 'src/app/components/spine-report/components/image-viewer/image-viewer.component';

@Component({
  selector: 'app-detail-tab',
  templateUrl: './detail-tab.component.html',
  styleUrls: ['../../spine-report.component.scss', './detail-tab.component.scss']
})
export class DetailTabComponent implements OnInit {

  @Input() axialImages: ImageUrls;
  @Input() sagittalImages: ImageUrls;
  @Input() report;

  axialIndex = 0;
  sagittalIndex = 0;
  showSegmentation = true;
  // If true, invert axial image sequence. (Used to display slices top to bottom)
  reverseAxial: boolean;

  constructor() { }

  ngOnInit(): void {
    if (this.sagittalImages &&
        this.sagittalImages.rawUrls &&
        typeof this.sagittalImages.rawUrls != 'string') {
      this.sagittalIndex = (this.sagittalImages.rawUrls.length - 1) / 2;
    }

    this.axialIndex = this.getInitialAxialSlice();

    if (this.report) {
      let imagePositions = this.report.canal_segmentation.image_positions;
      this.reverseAxial = true;
      if (imagePositions[0][2] > imagePositions[imagePositions.length - 1][2]) {
        this.reverseAxial = false;
      }
    }
  }

  /**
   * Returns the first interesting axial slice to show the user.
   */
  getInitialAxialSlice(): number {
    if (this.report &&
        this.axialImages &&
        typeof this.axialImages.rawUrls != 'string') {
      let numAxial = this.axialImages.rawUrls.length;

      // Return the most narrow slice > 0.
      let axialSlice = 0;
      let maxNarrowing = 0;
      this.report.measurements.canal_narrowing.narrowing.forEach((narrowing, i) => {
        if (narrowing < 1.0 && narrowing > maxNarrowing) {
          axialSlice = i;
          maxNarrowing = narrowing;
        }
      });
      return axialSlice;
    }
    return 0;
  }

  setAxialIndex(i: number) {
    this.axialIndex = i;
  }

  setSagittalIndex(i: number) {
    this.sagittalIndex = i;
  }

}
