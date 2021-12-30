import { Component, OnInit, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

import { fadeInAndOut } from 'src/app/helpers/animations';

import { JSONReport, ApiService } from 'src/app/services/api/api.service';

import { ImageUrls } from 'src/app/components/spine-report/components/image-viewer/image-viewer.component';

@Component({
  selector: 'app-spine-report',
  templateUrl: './spine-report.component.html',
  styleUrls: ['./spine-report.component.scss'],
  animations: [fadeInAndOut]
})
export class SpineReportComponent implements OnInit {

  studyId: string;
  studyName: string;

  tab = 1;
  share = false;
  menu = false;

  reportDone = false;
  sagittalDone = false;
  report: JSONReport;
  images: ImageUrls;
  sagittalImages: ImageUrls;

  constructor(
    public route: ActivatedRoute,
    public api: ApiService) { }

  ngOnInit(): void {
    this.studyId = this.route.snapshot.paramMap.get('study_id');

    this.api.getStudy(this.studyId, 'deep')
      .subscribe((study) => {
        this.api.getReportJsonFromStudy(study).subscribe((report) => {
          this.report = report;
          this.reportDone = true;
        });

        this.studyName = study.name;
        this.images = {
          rawUrls: this.api.getImageLinksFromSeries(
            study.CanalSegmentations[0].Segmentation.PreprocessedSeries),
          segUrls: this.api.getImageLinksFromSeries(
            study.CanalSegmentations[0].Segmentation.PostprocessedSeries)
        };
      });

    this.api.getStudy(this.studyId, 'includeDisk')
      .subscribe((study) => {
        this.sagittalImages = {
          rawUrls: this.api.getImageLinksFromSeries(
            study.DiskSegmentations[0].Segmentation.PreprocessedSeries),
          segUrls: this.api.getImageLinksFromSeries(
            study.DiskSegmentations[0].Segmentation.PostprocessedSeries)
        };
        this.sagittalDone = true;
      });
  }

  onDialogClose(data) {
    console.log(data);
    this.share = false;
  }

  onMenuClose() {
    this.menu = false;
  }

  openDialog(e: Event) {
    e.stopPropagation();
    this.share = true;
  }
  openMenu(e: Event) {
    e.stopPropagation();
    this.menu = !this.menu;
  }

}
