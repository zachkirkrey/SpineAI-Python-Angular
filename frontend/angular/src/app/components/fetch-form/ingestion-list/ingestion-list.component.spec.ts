import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IngestionListComponent } from './ingestion-list.component';

describe('IngestionListComponent', () => {
  let component: IngestionListComponent;
  let fixture: ComponentFixture<IngestionListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IngestionListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IngestionListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
