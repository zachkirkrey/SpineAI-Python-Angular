import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { LegacyReportComponent } from './legacy-report.component';

describe('LegacyReportComponent', () => {
  let component: LegacyReportComponent;
  let fixture: ComponentFixture<LegacyReportComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ LegacyReportComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LegacyReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
