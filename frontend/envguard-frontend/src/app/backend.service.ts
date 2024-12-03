import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  public apiUrl : string = 'http://localhost:3000';
  constructor() { }
}
