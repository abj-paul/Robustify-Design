import { Injectable } from '@angular/core';
import { User } from './models/User';

@Injectable({
  providedIn: 'root'
})
export class ConstantService {
  currUser: User = new User();
  constructor() { }

  setUser(user: User): void {
    console.log("Setting new user --> " + user);
    this.currUser = user;
  }

  getUser(): User {
    return this.currUser;
  }
}
