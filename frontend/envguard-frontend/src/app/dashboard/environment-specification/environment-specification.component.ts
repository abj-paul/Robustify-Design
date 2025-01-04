import { Component } from '@angular/core';
import { SpecTemplateComponent } from '../spec-template/spec-template.component';

@Component({
  selector: 'app-environment-specification',
  imports: [SpecTemplateComponent],
  templateUrl: './environment-specification.component.html',
  styleUrl: './environment-specification.component.css'
})
export class EnvironmentSpecificationComponent {

}
