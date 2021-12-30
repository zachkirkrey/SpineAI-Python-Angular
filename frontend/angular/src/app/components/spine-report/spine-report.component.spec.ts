import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpineReportComponent } from './spine-report.component';

describe('SpineReportComponent', () => {
  let component: SpineReportComponent;
  let fixture: ComponentFixture<SpineReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpineReportComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpineReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
