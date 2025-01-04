import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RobustificationComponent } from './robustification.component';

describe('RobustificationComponent', () => {
  let component: RobustificationComponent;
  let fixture: ComponentFixture<RobustificationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RobustificationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RobustificationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
