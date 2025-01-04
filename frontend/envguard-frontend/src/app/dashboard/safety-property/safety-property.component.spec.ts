import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SafetyPropertyComponent } from './safety-property.component';

describe('SafetyPropertyComponent', () => {
  let component: SafetyPropertyComponent;
  let fixture: ComponentFixture<SafetyPropertyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SafetyPropertyComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SafetyPropertyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
