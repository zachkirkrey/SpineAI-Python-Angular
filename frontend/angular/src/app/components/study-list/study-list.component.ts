import { Component, OnInit, QueryList, ViewChildren } from '@angular/core';

import { ExportService } from 'src/app/services/export/export.service';

import { environment } from 'src/environments/environment';
import * as moment from 'moment';

@Component({
    selector: 'app-study-list',
    templateUrl: './study-list.component.html',
    styleUrls: ['./study-list.component.scss']
})
export class StudyListComponent implements OnInit {



    constructor(
        private exportService: ExportService) { }

    readonly api_url = environment.api_url;
    readonly index_url = `${environment.api_url}/studies?count=1000&scope=includeReports`;

    old_index=0
    report_index = [];
    index_complete = false;
    index_error: string;
    section: string = '';
    isShown: boolean = true;
    visibility: Boolean = true;
    action = []
    report_action = []
    action_index = []
   actionList = ['Scheduled for Clinic', 'Surgery', 'Additional Testing', 'Injections', 'Physical Therapy', 'RTC/DC', 'Referral']

    @ViewChildren('report_rows') report_rows: QueryList<any>;

    ngOnInit() {
        this.section = 'Hide patient name';
        function sort_by_creation(x, y) {
            return -1;
            if (x.creation_datetime > y.creation_datetime) {
            }
            if (x.creation_datetime < y.creation_datetime) {
                return 1;
            }
            return 0;
        }

        $.ajax({
            // TODO(billy): Create a dev config for this url so this can work during
            // development.
            url: this.index_url,
            dataType: 'json',
        }).done(function (data) {
            if ('error' in data) {
                this.index_error = data['error'];
            } else {
                //this.report_index = data;
                this.report_index = [{ 'creation_datetime': '2021-12-16', 'name': 'dicom_ucla', 'patient_name': 'Anonymous', 'Reports': [], 'id': '656' }, { 'creation_datetime': '2021-12-16', 'name': 'dicom_ucla', 'patient_name': 'Anonymous', 'Reports': [], 'id': '656' }, { 'creation_datetime': '2021-12-16', 'name': 'dicom_ucla', 'patient_name': 'Anonymous', 'Reports': [], 'id': '656' }, { 'creation_datetime': '2021-12-16', 'name': 'dicom_ucla', 'patient_name': 'Anonymous', 'Reports': [], 'id': '656' }]
                console.log("index", this.report_index);
                data.forEach(element => {
                    element.Reports = element.Reports.filter(report => report.type == 'PDF_SIMPLE');
                    element.Reports.sort(sort_by_creation);
                    //element.CanalSegmentations.sort(sort_by_creation);
                });
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${this.index_url}.`;
        }.bind(this)).always(() => {
            this.index_complete = true;
        });
    }

    dep = []
    new_index: any;
    actionValues(value, index) {
        this.new_index = index
        if(this.new_index === this.old_index){
         const obj=   {
                'time': moment(new Date()).format('DD/MM/YY hh:m'),
                'name': value
            }
            this.dep.push(obj);
            this.old_index = this.new_index
            this.report_action[index]= this.dep
        } else{
            this.dep =[]
            const obj=   {
                'time': moment(new Date()).format('DD/MM/YY hh:m'),
                'name': value
            }
            this.dep.push(obj);
            this.report_action[index]=this.dep
            this.old_index = this.new_index
        }
        console.log('Indexx',this.report_action)
    }

    toggleDisplay(event) {
        console.log("event", event);
        // this.visibility = false;
        // this.isShown = false;
        if (event.checked == true) {
            this.isShown = false;
            this.section = 'Show patient name';
        } else if (event.checked == false) {
            this.isShown = true;
            this.section = 'Hide patient name';
        }
        // this.isShown=!this.isShown;
        // console.log("show", this.isShown);
        // if(this.isShown) {
        //  this.section = 'Show patient name';
        // } else if(!this.isShown) {
        //   this.section = 'Hide patient name';

        // }
    }


    // boggleDisplay(){
    //  this.isShown = true;
    //  this.visibility = true;
    //  console.log("show", this.isShown);

    // }


    ngAfterViewInit() {
        // Ellipsis renderer for datatables.net from
        // https://datatables.net/blog/2016-02-26.
        let render_ellipsis = function (cutoff, ellipsis, wordbreak, escapeHtml) {
            var esc = function (t) {
                return t
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;');
            };

            return function (d, type, row) {
                // Order, search and type get the original data
                if (type !== 'display') {
                    return d;
                }

                if (typeof d !== 'number' && typeof d !== 'string') {
                    return d;
                }

                d = d.toString(); // cast numbers

                if (d.length < cutoff) {
                    return d;
                }

                var shortened = d.substr(0, cutoff - 1);

                // Find the last white space character in the string
                if (wordbreak) {
                    shortened = shortened.replace(/\s([^\s]*)$/, '');
                }

                // Protect against uncontrolled HTML input
                if (escapeHtml) {
                    shortened = esc(shortened);
                }
                if (ellipsis) {
                    return '<span class="ellipsis" title="' + esc(d) + '">' + shortened + '&#8230;</span>';
                }
                return '<span class="ellipsis" title="' + esc(d) + '">' + shortened + '</span>';
            };

        };

        function load_recommendation() {
            $('.recommendation_cell').each(function (i, elem) {
                let id = $(elem).data('study-id');
                $.ajax({
                    url: environment.api_url + `/reports?Studies.id=${id}&type=PDF_SIMPLE`,
                    dataType: 'json'
                })
                    .done(function (data) {
                        if (!data || !data.length) {
                            $(elem).html('Unknown');
                        } else {
                            if (data[0].surgery_recommended) {
                                $(elem).html('<span style="color: red;">Schedule Consultation</span>');
                            } else {
                                $(elem).html('No Consultation');
                            }
                        }
                    });
            });
        }

        this.report_rows.changes.subscribe(t => {
            $('#reports_table').DataTable({
                pageLength: 25,
                order: [[0, 'desc']],
                columnDefs: [{
                    // Only render date component of Created.
                    targets: 0,
                    render: render_ellipsis(11, false, false, false)
                }, {
                    // Render Study UID with ellipsis.
                    targets: 2,
                    render: render_ellipsis(15, true, false, false)
                }]
            });

            $('#reports_table').on('draw.dt', load_recommendation);

            load_recommendation();
        });
    }

    public exportCSV() {
        let csvContent = this.exportService.getCsvExport(this.report_index);
        let encodedUri = encodeURI(csvContent);
        let link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'spineai_export.csv');
        document.body.appendChild(link);
        link.click();
    }

}
