import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConstantService } from '../constant.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-project-list',
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.css'],
  imports: [CommonModule]
})
export class ProjectListComponent implements OnInit {
  projects = [
    { id: 1, title: 'Project Alpha' },
    { id: 2, title: 'Project Beta' },
    { id: 3, title: 'Project Gamma' },
  ];

  constructor(private router: Router, private constantService: ConstantService) {}

  ngOnInit(): void {
    console.log(this.constantService.getUser());
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Unauthorized access. Redirecting to login.');
      this.router.navigate(['/login']);
    }
  }

  createProject() {
    alert('Create Project functionality will be implemented here.');
    // Future functionality for project creation
  }

  openDashboard(projectId: number) {
    this.router.navigate(['/dashboard'], { queryParams: { projectId } });
  }
}
