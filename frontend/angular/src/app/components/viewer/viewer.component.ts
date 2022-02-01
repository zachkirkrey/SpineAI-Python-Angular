import { Component, OnInit, Input } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Router, ActivatedRoute } from '@angular/router';
import { ThrowStmt } from '@angular/compiler';


@Component({
    selector: 'app-viewer',
    templateUrl: './viewer.component.html',
    styleUrls: ['./viewer.component.sass']
})
export class ViewerComponent implements OnInit {
    readonly index_url = `${environment.api_url}/studies?count=1000&scope=includeReports`;
    token: any;
    score: number = 2;
    threshold: number = 6;
    score_max: number = 10;
    score_percentage = 0;
    threshold_percentage = 0;
    index: any;
    viewer_obj: any;
    index_data: any
    data_index = 0


    constructor(private router: Router, private route: ActivatedRoute) {
        this.token = localStorage.getItem('token')
        this.index_data = localStorage.getItem('index_data')
    }

    ngOnInit(): void {
        let obj: any
        obj = localStorage.getItem("patient_data")
        this.viewer_obj = JSON.parse(obj)
        console.log('viewer_obj', this.viewer_obj)
        function sort_by_creation(x, y) {
            return -1;
            if (x.creation_datetime > y.creation_datetime) {
            }
            if (x.creation_datetime < y.creation_datetime) {
                return 1;
            }
            return 0;
        }

        // TODO(billy): Create a dev config for this url so this can work during
        // development.
        $.ajax({
            url: this.index_url,
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            dataType: 'json',
        }).done(function (data) {
            if ('error' in data) {
                this.index_error = data['error'];
            } else {
                this.index = data;
                this.index.forEach(x => {
                    x.show_icon = false
                });
                data.forEach(element => {
                    element.Reports = element.Reports.filter(report => report.type == 'PDF_SIMPLE');
                    element.Reports.sort(sort_by_creation);
                });
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${this.index_url}.`;
        }.bind(this)).always(() => {
        });

        if (this.score > this.score_max) {
            this.score = this.score_max;
        }

        // TODO(billy): Support arithmetic errors.
        this.score_percentage = Math.round(this.score / this.score_max * 100);
        this.threshold_percentage = Math.round(this.threshold / this.score_max * 100);
    }

    get position() {
        return `calc(${this.score_percentage}% - 16px)`;
    }

    shuffle(array) {
        return array.sort(function () { return Math.random() - 0.5; });
    }
    nextItem() {
        this.index = JSON.parse(this.index_data)
        this.data_index = this.data_index + 1;
        this.data_index = this.data_index % this.index.length;
        this.viewer_obj = this.index[this.data_index]
        return this.viewer_obj;
    }
    prevItem() {
        if (this.data_index === 0) {
            this.data_index = this.index.length;
        }
        this.data_index = this.data_index - 1;
        this.viewer_obj = this.index[this.data_index]
        return this.viewer_obj;
    }
}
