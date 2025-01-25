import { Injectable } from '@angular/core';
import { User } from './models/User';
import { Project } from './models/Project';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConstantService {
  private currUser: User = new User();
  private currProject: Project = new Project();
  private activeTab: string = 'environment';

  constructor() {
    this.loadEnv();
   }

  setUser(user: User): void {
    console.log("Setting new user --> " + user);
    this.currUser = user;
  }

  getUser(): User {
    return this.currUser;
  }

  clearUser():void{
    this.currUser = new User();
  }

  setProject(project: Project){
    this.currProject = project;
  }

  getProject() : Project {
    return this.currProject;
  }

  getActiveTab(): string {
    return this.activeTab;
  }

  setActiveTab(activeTab: string): void {
    console.log("Upading active tab in constant service..");
    this.activeTab = activeTab;
  }

  private env: { [key: string]: string | undefined } = {};

  private loadEnv() {
    // Load environment variables from .env file
    this.env = {
      API_URL: environment.apiUrl,
      RECAPTCHA_KEY: environment.recaptchaKey_v2,
    };
  }

  getEnvVariable(key: string): string | undefined {
    return this.env[key];
  }
}
