import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientIntakeFormComponent } from './patient-intake-form.component';

describe('PatientIntakeFormComponent', () => {
  let component: PatientIntakeFormComponent;
  let fixture: ComponentFixture<PatientIntakeFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PatientIntakeFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientIntakeFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
