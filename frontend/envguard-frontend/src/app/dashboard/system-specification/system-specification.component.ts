import { Component } from '@angular/core';
import { SpecTemplateComponent } from "../spec-template/spec-template.component";

@Component({
  selector: 'app-system-specification',
  standalone: true,
  imports: [SpecTemplateComponent],
  templateUrl: './system-specification.component.html',
  styleUrl: './system-specification.component.css'
})
export class SystemSpecificationComponent {

}
