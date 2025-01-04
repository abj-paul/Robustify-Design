import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemSpecificationComponent } from './system-specification.component';

describe('SystemSpecificationComponent', () => {
  let component: SystemSpecificationComponent;
  let fixture: ComponentFixture<SystemSpecificationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SystemSpecificationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SystemSpecificationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
