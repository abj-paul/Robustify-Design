import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { CommonModule } from '@angular/common';

import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';


@Component({
  selector: 'app-report',
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.css'],
  imports: [CommonModule, MatCardModule, MatIconModule, MatListModule, MatProgressSpinnerModule]
})
export class ReportComponent implements OnInit {
  reports: string[] = [];
  loading: boolean = true;
  error: string | null = null;

  constructor(private http: HttpClient, private backendService: BackendService, private constantService: ConstantService) { }

  ngOnInit(): void {
    this.fetchReports();
  }

  fetchReports(): void {
    const url = `${this.backendService.apiUrl}/reports/${this.constantService.getProject().id}/`; // Your backend API endpoint

    this.http.get<any>(url).pipe(
      catchError((error) => {
        this.error = 'Failed to load reports';
        this.loading = false;
        return of(null);  // return an empty observable to avoid breaking the UI
      })
    ).subscribe(data => {
      if (data && data.reports) {
        this.reports = data.reports;
      }
      this.loading = false;
    });
  }

  openReport(reportUrl: string): void {
    window.open(reportUrl, '_blank');
  }
}
