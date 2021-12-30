import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpineRiskScoreBarComponent } from './spine-risk-score-bar.component';

describe('SpineRiskScoreBarComponent', () => {
  let component: SpineRiskScoreBarComponent;
  let fixture: ComponentFixture<SpineRiskScoreBarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SpineRiskScoreBarComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpineRiskScoreBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
