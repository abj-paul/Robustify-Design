import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BackendService {
  public apiUrl : string = `http://${environment.HOST_ADDRESS}:3000`;
  public secondApiUrl : string = `http://${environment.HOST_ADDRESS}:8000`;
  public userGuideUrl: string = `http://${environment.HOST_ADDRESS}:4201`;
  constructor() { }
}
