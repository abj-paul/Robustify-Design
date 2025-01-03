import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConstantService } from '../constant.service';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BackendService } from '../backend.service';
import { Project } from '../models/Project';
import { catchError, throwError } from 'rxjs';

@Component({
  selector: 'app-project-list',
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.css'],
  imports: [CommonModule]
})
export class ProjectListComponent implements OnInit {
  projects : Project[] = [];

  constructor(private router: Router, private constantService: ConstantService, private http: HttpClient, private backendService: BackendService) {}

  ngOnInit(): void {
    console.log(this.constantService.getUser());
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Unauthorized access. Redirecting to login.');
      this.router.navigate(['/login']);
    }
    this.loadProjectListForUser();
  }

  createProject() {
    alert('Create Project functionality will be implemented here.');
    // Future functionality for project creation
  }

  openDashboard(projectId: number) {
    this.router.navigate(['/dashboard'], { queryParams: { projectId } });
  }

  loadProjectListForUser(): void {
    const userId = this.constantService.getUser().userid;
    this.http
      .get<Project[]>(this.backendService.apiUrl+"/projects", { params: { "user_id": userId } })
      .pipe(
        catchError((error) => {
          console.error("Encountered error when loading projects for user.");
          return throwError(() => error);
        })
      )
      .subscribe((projects) => (this.projects = projects));
  }
  
}
