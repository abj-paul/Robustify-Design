import { Routes } from '@angular/router';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProjectListComponent } from './project-list/project-list.component';

export const routes: Routes = [
    {path: "register", component: RegisterComponent},
    {path: "login", component: LoginComponent},
    {path: "dashboard", component: DashboardComponent},
    {path: 'project-list', component: ProjectListComponent },
    {path: '**', redirectTo: '/login' }, // Fallback route
];
