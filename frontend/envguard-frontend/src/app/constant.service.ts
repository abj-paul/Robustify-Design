import { Injectable } from '@angular/core';
import { User } from './models/User';
import { Project } from './models/Project';

@Injectable({
  providedIn: 'root'
})
export class ConstantService {
  currUser: User = new User();
  currProject: Project = new Project();

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
}
