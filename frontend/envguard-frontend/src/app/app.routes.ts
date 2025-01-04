import { Routes } from '@angular/router';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProjectListComponent } from './project-list/project-list.component';
import { ConfigurationComponent } from './dashboard/configuration/configuration.component';
import { EnvironmentSpecificationComponent } from './dashboard/environment-specification/environment-specification.component';
import { SafetyPropertyComponent } from './dashboard/safety-property/safety-property.component';
import { SystemSpecificationComponent } from './dashboard/system-specification/system-specification.component';
import { RobustificationComponent } from './robustification/robustification.component';
import { ReportComponent } from './report/report.component';

export const routes: Routes = [
  { path: "register", component: RegisterComponent },
  { path: "login", component: LoginComponent },
  { path: 'project-list', component: ProjectListComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    children: [
      { path: '', redirectTo: 'environment', pathMatch: 'full' }, // Default child route
      { path: 'environment', component: EnvironmentSpecificationComponent },
      { path: 'system', component: SystemSpecificationComponent },
      { path: 'safety', component: SafetyPropertyComponent },
      { path: 'configuration', component: ConfigurationComponent },
      { path: 'robustification', component: RobustificationComponent },
      { path: 'reports', component: ReportComponent }
    ]
  },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' } // Default route
];