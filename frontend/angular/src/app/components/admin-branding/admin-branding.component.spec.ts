import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminBrandingComponent } from './admin-branding.component';

describe('AdminBrandingComponent', () => {
  let component: AdminBrandingComponent;
  let fixture: ComponentFixture<AdminBrandingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdminBrandingComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdminBrandingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
