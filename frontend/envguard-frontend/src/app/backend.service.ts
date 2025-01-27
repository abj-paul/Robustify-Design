import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  public apiUrl : string = 'http://192.168.0.106:3000';
  public userGuideUrl: string = 'http://192.168.0.106:4201';
  constructor() { }
}
