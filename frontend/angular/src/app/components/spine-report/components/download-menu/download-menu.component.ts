import { Component, ContentChildren, ElementRef, EventEmitter, Input, OnInit, Output, QueryList, ViewChild, ViewChildren } from '@angular/core';

@Component({
  selector: 'app-download-menu',
  templateUrl: './download-menu.component.html',
  styleUrls: ['../../spine-report.component.scss', './download-menu.component.scss'],
  host: {
    '(document:click)': 'onClick($event)',
  },
})
export class DownloadMenuComponent implements OnInit {

  @Input() el: HTMLElement;
  @Output() onClose = new EventEmitter(true);

  constructor(private elRef: ElementRef) { }

  onClick(event) {
    if (!this.elRef.nativeElement.contains(event.target)) {
      this.close();
    }
  }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    this.onClose.unsubscribe();
  }

  close() {
    this.onClose.emit(true);
  }

  get top() {
    return `${this.el.offsetTop + this.el.offsetHeight + 4}px`;
  }

  get left() {
    return `${this.el.offsetLeft}px`;
  }

}
