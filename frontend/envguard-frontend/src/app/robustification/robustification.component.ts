import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-robustification',
  templateUrl: './robustification.component.html',
  styleUrls: ['./robustification.component.css'],
  imports: [CommonModule]
})
export class RobustificationComponent {
  isLoading: boolean = false; // For progress indication
  isSuccess: boolean | null = null; // Track success or failure

  constructor(
    private http: HttpClient,
    private backendService: BackendService,
    private constantService: ConstantService
  ) {}

  runFortis() {
    this.isLoading = true;
    this.isSuccess = null; // Reset the success status
    const classList : string [] = []; 

    const formData = new FormData();
    // Only append class_list if it's not null
    if (classList && classList.length > 0) {
      formData.append('class_list', JSON.stringify(classList));
    } else {
      formData.append('class_list', '');  // Send empty array instead of null
    }

    this.http.post(`${this.backendService.apiUrl}/projects/${this.constantService.getProject().id}/execute`, formData)
      .subscribe({
        next: (response) => {
          console.log('Robustification Successful:', response);
          this.isSuccess = true;
        },
        error: (error) => {
          console.error('Robustification failed:', error);
          this.isSuccess = false;
        },
        complete: () => {
          this.isLoading = false;
        },
      });
  }
}
