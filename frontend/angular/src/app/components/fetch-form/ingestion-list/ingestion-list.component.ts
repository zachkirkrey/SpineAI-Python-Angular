import { Component, OnInit, QueryList, ViewChildren } from '@angular/core';

import { ApiService } from 'src/app/services/api/api.service';

@Component({
  selector: 'app-ingestion-list',
  templateUrl: './ingestion-list.component.html',
  styleUrls: ['./ingestion-list.component.scss']
})
export class IngestionListComponent implements OnInit {

  constructor(
    private api: ApiService) { }

  @ViewChildren('ingestion_rows') ingestion_rows: QueryList<any>;

  ingestions: Array<any>;
  tableReady: boolean;

  ngOnInit(): void {
    this.api.getFetchIngestions()
      .subscribe(ingestions => this.loadIngestions(ingestions));
  }

  loadIngestions(ingestions) {
    this.ingestions = ingestions;
    this.tableReady = true;
  }

  ngAfterViewInit() {
    // this.ingestion_rows.changes.subscribe(t => {
    //   $('#ingestions_table').DataTable({
    //     pageLength: 25,
    //     order: [[ 1, 'desc' ]]
    //   });
    // });
  }

}
