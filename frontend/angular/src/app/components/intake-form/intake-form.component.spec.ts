import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { IntakeFormComponent } from './intake-form.component';

describe('IntakeFormComponent', () => {
  let component: IntakeFormComponent;
  let fixture: ComponentFixture<IntakeFormComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [ IntakeFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IntakeFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
