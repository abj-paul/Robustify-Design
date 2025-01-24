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
import { ChatComponent } from './chat/chat.component';
import { CreateProjectComponent } from './create-project/create-project.component';
import { AuthInterceptor } from './auth.interceptor';
import { AuthGuard } from './auth-guard.service';

export const routes: Routes = [
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { 
    path: 'create-project', 
    component: CreateProjectComponent,
    canActivate: [AuthGuard] // Add authentication guard
  },
  { 
    path: 'project-list', 
    component: ProjectListComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: '', 
    redirectTo: 'login', 
    pathMatch: 'full' 
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard], // Protect the entire dashboard route
    children: [
      { path: '', redirectTo: 'environment', pathMatch: 'full' },
      { path: 'environment', component: EnvironmentSpecificationComponent },
      { path: 'system', component: SystemSpecificationComponent },
      { path: 'safety', component: SafetyPropertyComponent },
      { path: 'configuration', component: ConfigurationComponent },
      { path: 'robustification', component: RobustificationComponent },
      { path: 'reports', component: ReportComponent },
      { path: 'chat', component: ChatComponent }
    ]
  },
  // Add a catch-all route to redirect to login for any undefined routes
  { path: '**', redirectTo: 'login' }
];