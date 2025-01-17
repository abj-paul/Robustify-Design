import { Injectable } from '@angular/core';
import { User } from './models/User';
import { Project } from './models/Project';

@Injectable({
  providedIn: 'root'
})
export class ConstantService {
  private currUser: User = new User();
  private currProject: Project = new Project();
  private activeTab: string = 'environment';

  constructor() { }

  setUser(user: User): void {
    console.log("Setting new user --> " + user);
    this.currUser = user;
  }

  getUser(): User {
    return this.currUser;
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
}
