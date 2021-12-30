import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild
} from '@angular/core';

export interface ImageUrls {
  rawUrls: string | Array<string>;
  segUrls: string | Array<string>;
}

@Component({
  selector: 'app-image-viewer',
  templateUrl: './image-viewer.component.html',
  styleUrls: ['../../spine-report.component.scss', './image-viewer.component.scss'],
})
export class ImageViewerComponent implements AfterViewInit, OnInit {

  @Input() images: ImageUrls;
  // cutlines[local_slice][foreign_slice][point][row|col]
  @Input() cutlines: Array<Array<Array<Array<number>>>>;
  @Input() cutlineIndex: number;
  @Input() reverse = false;

  @Input() label: string;
  @Input() showSegmentation: boolean;
  @Input() index = 0;

  @Output() indexChanged = new EventEmitter<number>(true);

  cutlinesEnabled = false;
  cutlineCanvasHeight = 256;
  cutlineCanvasWidth = 256;
  @ViewChild('cutlineCanvas', {static: false}) cutlineCanvas: ElementRef;
  cutlineContext: CanvasRenderingContext2D;

  numImages: number;
  showControls: boolean;
  brightness = 1;

  constructor() { }

  ngOnInit(): void {
    if (typeof this.images.rawUrls == "string") {
      this.numImages = 1;
    } else {
      this.label = (this.getVisualIndex() + 1).toString();
      this.numImages = this.images.rawUrls.length;
      this.showControls = true;
      document.documentElement.style.setProperty('--thumb-width', `calc(100% / ${this.images.rawUrls.length})`);
    }

    this.enableCutlines();
  }

  ngAfterViewInit(): void {
    if (this.cutlineCanvas) {
      this.cutlineContext = this.cutlineCanvas.nativeElement.getContext('2d');
    }
    this.drawCutline();
  }

  ngOnChanges(changes) {
    for (const propName in changes) {
      if (propName == 'index') {
        this.changeIndex(false);
      }
      if (propName == 'cutlineIndex') {
        this.drawCutline();
      }
    }
  }

  ngOnDestroy(): void {
    this.indexChanged.unsubscribe();
  }

  getVisualIndex(): number {
    if (this.reverse) {
      return this.images.rawUrls.length - 1 - this.index;
    }
    return this.index
  }

  changeIndex(emit = true) {
    this.label = (this.getVisualIndex() + 1).toString();
    this.drawCutline();
    if (emit) this.indexChanged.emit(this.index);
  }

  enableCutlines(): void {
    // TODO(billy): Perform input validation here.
    this.cutlinesEnabled = (this.cutlines && this.cutlineIndex != null);
  }

  drawCutline(): void {
    if (!this.cutlinesEnabled || !this.cutlineContext) return;

    let cutline = this.cutlines[this.index][this.cutlineIndex];

    let ctx = this.cutlineContext;
    ctx.clearRect(0, 0, this.cutlineCanvasWidth, this.cutlineCanvasHeight);
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    ctx.beginPath();
    try {
      ctx.moveTo(cutline[0][1], cutline[0][0]);
      ctx.lineTo(cutline[1][1], cutline[1][0]);
    } catch (error) {
      console.error(error);
      console.error(
        `Could not draw cutline with given index [${this.index}][${this.cutlineIndex}]`);
    }
    ctx.stroke();
  }

  setBrightness(val: number) {
    this.brightness += val;
  }

  slide(val: number) {
    const current = this.index + val;
    if (current < 0) {
      this.index = 0;
    } else if (current > this.images.rawUrls.length - 1) {
      this.index = this.images.rawUrls.length - 1;
    } else {
      this.index = current;
    }
    this.indexChanged.emit(this.index);
  }

  setImage(images: any): string {
    if (typeof images === "string") {
      return `url(${images})`;
    } else {
      return `url(${images[this.index]})`;
    }
  }

}
