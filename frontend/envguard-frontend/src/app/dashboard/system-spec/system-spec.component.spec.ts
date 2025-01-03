import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemSpecComponent } from './system-spec.component';

describe('SystemSpecComponent', () => {
  let component: SystemSpecComponent;
  let fixture: ComponentFixture<SystemSpecComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SystemSpecComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SystemSpecComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
