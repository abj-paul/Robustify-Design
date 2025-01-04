import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { CommonModule } from '@angular/common';
import { SpecTemplateComponent } from './spec-template/spec-template.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  standalone: true,
  imports: [MatTabsModule, CommonModule, SpecTemplateComponent],
})
export class DashboardComponent implements OnInit {
  projectId: number | null = null;
  projectTitle: string | null = null;

  constructor(private route: ActivatedRoute, private router: Router) {}

  ngOnInit(): void {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Unauthorized access. Redirecting to login.');
      this.router.navigate(['/login']);
      return;
    }

    this.route.queryParams.subscribe((params) => {
      this.projectId = params['projectId'];
      if (!this.projectId) {
        alert('Invalid project. Redirecting to project list.');
        this.router.navigate(['/project-list']);
      }
    });
  }
}
