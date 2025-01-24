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
  imports: [CommonModule, MatCardModule, MatIconModule, MatListModule, MatProgressSpinnerModule],
})
export class ReportComponent implements OnInit {
  reports: string[] = [];
  loading: boolean = true;
  error: string | null = null;

  constructor(private http: HttpClient, private backendService: BackendService, private constantService: ConstantService) {}

  ngOnInit(): void {
    this.fetchReports();
  }

  fetchReports(): void {
    const url = `${this.backendService.apiUrl}/reports/${this.constantService.getProject().id}/`; // Your backend API endpoint

    this.http
      .get<any>(url)
      .pipe(
        catchError((error) => {
          this.error = 'Failed to load reports';
          this.loading = false;
          return of(null); // Return an empty observable to avoid breaking the UI
        })
      )
      .subscribe((data) => {
        if (data && data.reports) {
          this.reports = this.sortReportsByDate(data.reports);
        }
        this.loading = false;
      });
  }

  sortReportsByDate(reports: string[]): string[] {
    return reports.sort((a, b) => {
      const dateA = this.extractDateFromFilename(a);
      const dateB = this.extractDateFromFilename(b);
      return dateB.getTime() - dateA.getTime(); // Sort descending
    });
  }
  
  
  extractDateFromFilename(filename: string): Date {
    const match = filename.match(/(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})/);
    if (match) {
      // Reconstruct date string in a format Date constructor can parse
      const dateString = `${match[1]}T${match[2].replace(/-/g, ':')}Z`;
      const parsedDate = new Date(dateString);
      console.log(`Match found and converted to date ${new Date(parsedDate)}`)
      return isNaN(parsedDate.getTime()) ? new Date(0) : parsedDate;
    }
    return new Date(0);
  }

  openReport(reportUrl: string): void {
    window.open(reportUrl, '_blank');
  }
}
