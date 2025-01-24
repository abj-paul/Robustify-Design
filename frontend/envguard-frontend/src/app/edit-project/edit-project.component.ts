import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-edit-project',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './edit-project.component.html',
  styleUrl: './edit-project.component.css'
})
export class EditProjectComponent implements OnInit{

  projectForm: FormGroup;
  projectId: number = 1;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router,
    private backendService: BackendService,
    private constantService: ConstantService
  ) {
    this.projectForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: ['']
    });
  }

  ngOnInit() {
    this.projectId = this.constantService.getProject().id;
    this.loadProjectDetails();
  }

  loadProjectDetails() {
    const userId = this.constantService.getUser().userid;
    this.http.get(`${this.backendService.apiUrl}/projects/${this.projectId}?user_id=${userId}`)
      .subscribe({
        next: (project: any) => {
          this.projectForm.patchValue({
            name: project.name,
            description: project.description
          });
        },
        error: (error) => {
          console.error('Error loading project:', error);
          this.router.navigate(['/project-list']);
        }
      });
  }

  updateProject() {
    if (this.projectForm.valid) {
      const userId = this.constantService.getUser().userid;
      this.http.put(`${this.backendService.apiUrl}/projects/${this.projectId}?user_id=${userId}`, this.projectForm.value)
        .subscribe({
          next: () => {
            this.router.navigate(['/project-list']);
          },
          error: (error) => {
            console.error('Error updating project:', error);
            alert('Failed to update project');
          }
        });
    }
  }

  deleteProject() {
    if (confirm('Are you sure you want to delete this project?')) {
      const userId = this.constantService.getUser().userid;
      this.http.delete(`${this.backendService.apiUrl}/projects/${this.projectId}?user_id=${userId}`)
        .subscribe({
          next: () => {
            this.router.navigate(['/project-list']);
          },
          error: (error) => {
            console.error('Error deleting project:', error);
            alert('Failed to delete project');
          }
        });
    }
  }
 
}
