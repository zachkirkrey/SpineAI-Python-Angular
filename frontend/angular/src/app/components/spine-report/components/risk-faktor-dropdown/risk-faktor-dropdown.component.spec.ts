import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskFaktorDropdownComponent } from './risk-faktor-dropdown.component';

describe('RiskFaktorDropdownComponent', () => {
  let component: RiskFaktorDropdownComponent;
  let fixture: ComponentFixture<RiskFaktorDropdownComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RiskFaktorDropdownComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RiskFaktorDropdownComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
