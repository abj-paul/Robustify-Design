import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-project',
  standalone: true,
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.css'],
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
})
export class CreateProjectComponent {
  projectForm: FormGroup;

  constructor(
    private fb: FormBuilder, 
    private http: HttpClient, 
    private backendService: BackendService,
    private constantService: ConstantService,
    private router: Router
  ) {
    this.projectForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: ['']
    });
  }

  createProject(): void {
    if (this.projectForm.valid) {
      const userId = this.constantService.getUser().userid;
      
      this.http.post(`${this.backendService.apiUrl}/projects?user_id=${userId}`, this.projectForm.value).subscribe({
        next: (response) => {
          console.log('Project created successfully:', response);
          this.router.navigate(['/project-list']);
        },
        error: (error) => {
          console.error('Error creating project:', error);
          alert('Failed to create project: ' + error.message);
        }
      });
    } else {
      alert('Please fill out the form correctly.');
    }
  }
}