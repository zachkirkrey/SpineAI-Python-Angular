import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailBarsComponent } from './detail-bars.component';

describe('DetailBarsComponent', () => {
  let component: DetailBarsComponent;
  let fixture: ComponentFixture<DetailBarsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DetailBarsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DetailBarsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
