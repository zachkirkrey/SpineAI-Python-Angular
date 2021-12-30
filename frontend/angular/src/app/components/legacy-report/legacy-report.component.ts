import { Component, Injectable, OnInit, Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';

import { UploadService, UploadStatus } from 'src/app/services/upload/upload.service';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

import { environment } from 'src/environments/environment';

// TODO(billy): Store in map instead.
const upload_complete_msg = 'Preprocessing study...';
const preprocessing_complete_msg = 'Preprocessing complete. Classifying study...';
const segmentation_complete_msg = 'Classification complete.';

// Make jQuery available here.
declare var $: any;

@Pipe({ name: 'safe' })
export class SafePipe implements PipeTransform {
    constructor(private sanitizer: DomSanitizer) {}
    transform(url) {
          return this.sanitizer.bypassSecurityTrustResourceUrl(url);
        }
}

// Stores and makes available the last accessed studyId.
@Injectable()
export class LegacyReportData {
  studyId: string = '';
}

@Component({
  selector: 'app-legacy-report',
  templateUrl: './legacy-report.component.html',
  styleUrls: ['./legacy-report.component.scss']
})
export class LegacyReportComponent implements OnInit {

  constructor(
    public data: LegacyReportData,
    public route: ActivatedRoute) { }

  metadata;
  errorStr: string;
  reportUrl: string;
  reportCSVUrl: string;
  reportSimpleUrl: string;
  viewerUrl: string;

  // getMetadata(study_id: string) {
  //   $.ajax({
  //     url: `/static/uploads/${study_id}/metadata.json`
  //   }).done(function(data, textStatus, jqXHR) {
  //     this.metadata = data;
  //   }.bind(this));
  // }

  ngOnInit() {
    this.data.studyId = this.route.snapshot.paramMap.get('study_id');

    // $.ajax({
    //   url: `${environment.api_url}/reports?` +
    //     `type=PDF_SIMPLE&` +
    //     `sort=-creation_datetime&` +
    //     `Studies.uuid=${this.data.studyId}`
    // }).done(function(data, textStatus, jqXHR) {
    //   if (data.length) {
    //     let reportId = data[0].id;
    //     this.reportSimpleUrl = `${environment.api_url}/report/${reportId}?as=PDF`;
    //   } else {
    //     this.errorStr = `Could not find PDF report for Study "${this.data.studyId}"`;
    //   }
    // }.bind(this));
    // this.getMetadata(this.data.studyId);
    // this.reportUrl = `/static/uploads/${this.data.studyId}/report/report.pdf`;
    this.reportSimpleUrl = `${environment.api_url}/reports?as=PDF&` +
      "type=PDF_SIMPLE&sort=-creation_datetime&" +
      `Studies.uuid=${this.data.studyId}`;
    this.viewerUrl = `${environment.api_url}/reports?as=HTML&` +
      "type=HTML_VIEWER&sort=-creation_datetime&" +
      `Studies.uuid=${this.data.studyId}`;
    this.reportCSVUrl = `${environment.api_url}/reports?as=CSV&` +
      "type=JSON&sort=-creation_datetime&" +
      `Studies.uuid=${this.data.studyId}`;

  }
}
