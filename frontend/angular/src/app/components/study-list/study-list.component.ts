import { Component, OnInit, QueryList, ViewChildren } from '@angular/core';

import { ExportService } from 'src/app/services/export/export.service';

import { environment } from 'src/environments/environment';

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

  index = [];
  index_complete = false;
  index_error: string;

  @ViewChildren('report_rows') report_rows: QueryList<any>;

  ngOnInit() {
    function sort_by_creation(x, y) {
      if (x.creation_datetime > y.creation_datetime) {
        return -1;
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
    }).done(function(data) {
      if ('error' in data) {
        this.index_error = data['error'];
      } else {
        this.index = data;
        console.log("index", this.index);
        data.forEach(element => {
          element.Reports = element.Reports.filter(report => report.type == 'PDF_SIMPLE');
          element.Reports.sort(sort_by_creation);
          //element.CanalSegmentations.sort(sort_by_creation);
        });
      }
    }.bind(this)).fail(function(jqXHR, textStatus, errorThrown) {
      this.index_error = `Could not fetch search index from ${this.index_url}.`;
    }.bind(this)).always(() => {
      this.index_complete = true;
    });
  }

  ngAfterViewInit() {
    // Ellipsis renderer for datatables.net from
    // https://datatables.net/blog/2016-02-26.
    let render_ellipsis = function (cutoff, ellipsis, wordbreak, escapeHtml) {
      var esc = function (t) {
        return t
          .replace( /&/g, '&amp;' )
          .replace( /</g, '&lt;' )
          .replace( />/g, '&gt;' )
          .replace( /"/g, '&quot;' );
      };

      return function ( d, type, row ) {
        // Order, search and type get the original data
        if ( type !== 'display' ) {
          return d;
        }

        if ( typeof d !== 'number' && typeof d !== 'string' ) {
          return d;
        }

        d = d.toString(); // cast numbers

        if ( d.length < cutoff ) {
          return d;
        }

        var shortened = d.substr(0, cutoff-1);

        // Find the last white space character in the string
        if ( wordbreak ) {
          shortened = shortened.replace(/\s([^\s]*)$/, '');
        }

        // Protect against uncontrolled HTML input
        if ( escapeHtml ) {
          shortened = esc( shortened );
        }
        if (ellipsis) {
            return '<span class="ellipsis" title="'+esc(d)+'">'+shortened+'&#8230;</span>';
        }
        return '<span class="ellipsis" title="'+esc(d)+'">'+shortened+'</span>';
      };

    };

    function load_recommendation() {
      $('.recommendation_cell').each(function(i, elem) {
        let id = $(elem).data('study-id');
        $.ajax({
          url: environment.api_url + `/reports?Studies.id=${id}&type=PDF_SIMPLE`,
          dataType: 'json'
        })
        .done(function(data) {
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
        order: [[ 0, 'desc' ]],
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
    let csvContent = this.exportService.getCsvExport(this.index);
    let encodedUri = encodeURI(csvContent);
    let link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'spineai_export.csv');
    document.body.appendChild(link);
    link.click();
  }

}