import { Component, OnInit, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

import { fadeInAndOut } from 'src/app/helpers/animations';

import { JSONReport, ApiService } from 'src/app/services/api/api.service';

import { ImageUrls } from 'src/app/components/spine-report/components/image-viewer/image-viewer.component';
import { environment } from 'src/environments/environment';
import * as moment from 'moment';
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
    token: any
    sagittalImages: ImageUrls;
    fetchArr = []
    report_actions: any
    checked: boolean = true
    showCheckbox: boolean = true
    hideCheckboxMsg = 'Show patient info'
    readonly api_url = environment.api_url;

    constructor(
        public route: ActivatedRoute,
        public api: ApiService) { }

    ngOnInit(): void {
        this.studyId = this.route.snapshot.paramMap.get('study_id');
        this.token = localStorage.getItem('token')

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
        this.callAction(this.studyId)
    }
    callAction(id) {
        let patient_url = `${environment.api_url}/study/${id}?scope=includeActions`;
        $.ajax({
            url: patient_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            this.fetchArr.push(data)
            console.log('fetchArr', this.fetchArr)
            this.fetchArr.forEach(element => {
                element.appointment_date = moment(element.appointment_date).format("MM/DD/YY")
                element.date_of_birth = moment(element.date_of_birth).format("MM/DD/YY")
            });

        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${patient_url}.`;
        }.bind(this)).always(() => {
        });
    }
    toggleDisplay() {
        this.showCheckbox = !this.showCheckbox
    }
    onDialogClose(data) {
        console.log(data);
        this.share = false;
    }
    showViewer() {
        window.open(
            `${this.api_url}/reports?as=HTML&type=HTML_VIEWER&sort=-creation_datetime&Studies.uuid=${this.studyId}&${this.token}`, "_blank")
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
