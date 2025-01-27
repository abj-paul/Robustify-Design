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
    //alert('Create Project functionality will be implemented here.');
    this.router.navigate(['/create-project']);  }

  openDashboardForProject(project: Project) {
    this.constantService.setProject(project);
    console.log(`Current Project is $(project.name)`);
    this.router.navigate(['/dashboard'], { queryParams: { projectId: project.id } });
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
  logout(): void {
    this.http.post(`${this.backendService.apiUrl}/logout`, {}).subscribe({
      next: (response) => {
        console.log('Logout successful', response);
        
        // Clear user data from the constant service
        this.constantService.clearUser();
        
        // Remove the access token from local storage
        localStorage.removeItem('access_token');
        
        // Navigate to the login page
        this.router.navigate(['/login']);
      },
      error: (error) => {
        console.error('Logout failed', error);
      },
    });
  }
    // // Clear access token from local storage
    // localStorage.removeItem('access_token');
    
    // // Clear any user-related data from constant service
    // this.constantService.clearUser();
    
    // // Navigate back to login page
    // this.router.navigate(['/login']);
  //}
}
