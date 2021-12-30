import { Component, ElementRef, EventEmitter, OnInit, Output, ViewChild } from '@angular/core';

@Component({
  selector: 'app-share-dialog',
  templateUrl: './share-dialog.component.html',
  styleUrls: ['../../spine-report.component.scss', './share-dialog.component.scss'],
  host: {
    '(document:click)': 'onClick($event)',
  },
})
export class ShareDialogComponent implements OnInit {

  data = {
    email: "",
    message: "",
  }

  @Output() onClose = new EventEmitter(true);

  @ViewChild("dialog") dialog: ElementRef;

  constructor() { }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    this.onClose.unsubscribe();
  }

  onClick(event) {
    if (!this.dialog.nativeElement.contains(event.target)) {
      this.close(null);
    }
  }

  close(data: any) {
    this.onClose.emit(data);
  }

}
