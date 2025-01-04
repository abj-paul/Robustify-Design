import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnvironmentSpecificationComponent } from './environment-specification.component';

describe('EnvironmentSpecificationComponent', () => {
  let component: EnvironmentSpecificationComponent;
  let fixture: ComponentFixture<EnvironmentSpecificationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EnvironmentSpecificationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EnvironmentSpecificationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
