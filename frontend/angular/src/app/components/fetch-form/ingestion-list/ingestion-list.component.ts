import {Component, OnInit, QueryList, ViewChildren, Input, OnChanges, SimpleChanges} from '@angular/core';

import {ApiService, Ingestion} from 'src/app/services/api/api.service';
import {catchError} from "rxjs/operators";
import {of} from "rxjs";
import {Observable} from "rxjs/Observable";

@Component({
  selector: 'app-ingestion-list',
  templateUrl: './ingestion-list.component.html',
  styleUrls: ['./ingestion-list.component.scss']
})
export class IngestionListComponent implements OnInit, OnChanges {
  @Input() uuidId: string | undefined;

  constructor(
    private api: ApiService) { }

  // tslint:disable-next-line:variable-name
  @ViewChildren('ingestion_rows') ingestion_rows: QueryList<any>;

  ingestions: Array<Ingestion> = [];
  tableReady = true;

  ngOnInit(): void {
    this.loadIngestions();
  }

  loadIngestions() {
    if (this.uuidId) {
      this.tableReady = false;
      this.api.getFetchIngestions(this.uuidId)
        .pipe(
          catchError((err): Observable<Ingestion[]> => {
            console.error(err);
            return of([]);
          })
        )
        .subscribe(ingestions => {
          this.ingestions = ingestions;
          this.tableReady = true;
        });
    }
  }

  ngAfterViewInit() {
    // this.ingestion_rows.changes.subscribe(t => {
    //   $('#ingestions_table').DataTable({
    //     pageLength: 25,
    //     order: [[ 1, 'desc' ]]
    //   });
    // });
  }

  ngOnChanges(changes: SimpleChanges): void {
    // const {uuidId} = changes;
    // if ( uuidId) {
    //   this.loadIngestions();
    // }
  }
}
