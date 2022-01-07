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

    constructor(private exportService: ExportService) { }
    readonly api_url = environment.api_url;
    readonly index_url = `${environment.api_url}/studies?count=1000&scope=includeReports`;
    readonly action_save_url = `${environment.api_url}/action`;

    old_index = 0
    index = [];
    index_complete = false;
    index_error: string;
    action_error: string;
    section: string = '';
    isShown: boolean = true;
    visibility: Boolean = true;
    action = []
    report_action = []
    action_index = []
    dep = []
    new_index: any;
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
        // TODO(billy): Create a dev config for this url so this can work during
        // development.
        $.ajax({
            url: this.index_url,
            dataType: 'json',
        }).done(function (data) {
            if ('error' in data) {
                this.index_error = data['error'];
            } else {
                this.index = data;
                data.forEach(element => {
                    element.Reports = element.Reports.filter(report => report.type == 'PDF_SIMPLE');
                    element.Reports.sort(sort_by_creation);
                });
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.index_error = `Could not fetch search index from ${this.index_url}.`;
        }.bind(this)).always(() => {
            this.index_complete = true;
        });
    }

    saveAction(id, index) {
        let report_Arr = []
        report_Arr = this.report_action[index]
        report_Arr.forEach(element => {
            this.callSaveAPI(element.name, element.time, id)
        });
    }

    callSaveAPI(name, time, study_id) {
        let req_data = {
            "name": name,
            "creation_datetime": time,
            "study": parseInt(study_id)
        }
        $.ajax({
            url: this.action_save_url,
            dataType: 'json',
            type: "POST",
            data: req_data,
        }).done(function (data) {
            if ('error' in data) {
                this.action_error = data['error'];
            } else {
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.index_url}.`;
        }.bind(this)).always(() => {
        });
    }
    actionValues(value, index) {
        this.new_index = index
        if (this.new_index === this.old_index) {
            const obj = {
                'time': moment(new Date()).format("DD/MM/YY hh:mm a"),
                'name': value
            }
            this.dep.push(obj);
            this.old_index = this.new_index
            this.report_action[index] = this.dep
        } else {
            this.dep = []
            const obj = {
                'time': moment(new Date()).format("DD/MM/YY hh:mm a"),
                'name': value
            }
            this.dep.push(obj);
            this.report_action[index] = this.dep
            this.old_index = this.new_index
        }
    }

    toggleDisplay(event) {
        if (event.checked == true) {
            this.isShown = false;
            this.section = 'Show patient name';
        } else if (event.checked == false) {
            this.isShown = true;
            this.section = 'Hide patient name';
        }
    }
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
                retrieve: true,
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
                }],
                destroy: false
            });
            $('#reports_table').on('draw.dt', load_recommendation);
            load_recommendation();
        });
    }

    public exportCSV() {
        let csvContent = this.exportService.getCsvExport(this.index);
        let encodedUri = encodeURI(csvContent);
        let link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', 'spineai_export.csv');
        document.body.appendChild(link);
        link.click();
    }

}
