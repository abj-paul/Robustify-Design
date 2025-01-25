import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { BackendService } from '../backend.service';
import { ConstantService } from '../constant.service';
import { environment } from '../../environments/environment';
import { CommonModule } from '@angular/common';
import { NgxCaptchaModule } from 'ngx-captcha';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [CommonModule, ReactiveFormsModule, NgxCaptchaModule]
})
export class LoginComponent {
  loginForm: FormGroup;
  siteKey = environment.recaptchaKey_v2; // Your reCAPTCHA site key from environment.ts
  captchaVerified = false;
  captchaResponse: string | null = null;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private backendService: BackendService,
    private router: Router,
    private constantService: ConstantService
  ) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
    });
  }

  onCaptchaResolved(response: string): void {
    this.captchaResponse = response;
    this.captchaVerified = !!response;
    console.log('CAPTCHA resolved:', response);
  }

  onSubmit(): void {
    if (this.loginForm.valid && this.captchaVerified) {
      const { username, password } = this.loginForm.value;

      // Optionally pass the CAPTCHA token to your backend for verification
      this.http
        .post(this.backendService.apiUrl + '/login', {
          username,
          password,
          //captchaToken: this.captchaResponse, // Include CAPTCHA token if backend verification is added
        })
        .pipe(
          catchError((error) => {
            console.error('Login failed', error);
            return throwError(error);
          })
        )
        .subscribe({
          next: (response: any) => {
            console.log('Login successful', response);
            localStorage.setItem('access_token', response.access_token);

            this.constantService.setUser({
              userid: response.user.id,
              username: response.user.username,
              organization: response.user.organization,
            });
            this.router.navigate(['/project-list']);
          },
          error: (error) => {
            console.error('Error:', error);
            alert(error.error.detail || 'Login failed!');
          },
        });
    } else {
      console.log('Form is invalid or CAPTCHA not verified');
    }
  }
}
