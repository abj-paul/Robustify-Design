// dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { CommonModule } from '@angular/common';
import { SpecTemplateComponent } from './spec-template/spec-template.component';
import { SystemSpecificationComponent } from './system-specification/system-specification.component';
import { EnvironmentSpecificationComponent } from './environment-specification/environment-specification.component';
import { SafetyPropertyComponent } from './safety-property/safety-property.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { RobustificationComponent } from '../robustification/robustification.component';
import { ReportComponent } from '../report/report.component';
import { ConstantService } from '../constant.service';
//import { AuthService } from '../auth.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  standalone: true,
  imports: [
    MatTabsModule,
    CommonModule,
    RouterModule,
    SystemSpecificationComponent,
    EnvironmentSpecificationComponent,
    SafetyPropertyComponent,
    ConfigurationComponent,
    RobustificationComponent,
    ReportComponent
  ],
})
export class DashboardComponent implements OnInit {
  projectId: number | null = null;
  projectTitle: string | null = null;
  activeTab = 'environment';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private constantService: ConstantService,
    //private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Check authentication status
    // if (!this.authService.isAuthenticated()) {
    //   this.router.navigate(['/login']);
    //   return;
    // }

    this.projectTitle = this.constantService.getProject()?.name;
    this.projectId = this.constantService.getProject()?.id;

    if (!this.projectId) {
      this.router.navigate(['/project-list']);
      return;
    }

    // Subscribe to route changes to update active tab
    this.router.events.subscribe(() => {
      const currentUrl = this.router.url.split('/').pop() || 'environment';
      this.activeTab = currentUrl;
      this.constantService.setActiveTab(this.activeTab);
    });
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
    this.constantService.setActiveTab(tab);
    this.router.navigate([`/dashboard/${tab}`]);
  }

  edit_project() {
    //alert('Create Project functionality will be implemented here.');
    this.router.navigate(['/edit-project']);  
  }


  goBackToProjectList() {
    //alert('Create Project functionality will be implemented here.');
    this.router.navigate(['/project-list']);  
  }
}