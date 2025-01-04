import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { BackendService } from '../backend.service';
import { Router } from '@angular/router';
import { ConstantService } from '../constant.service';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [FormsModule, ReactiveFormsModule, CommonModule],
})

export class LoginComponent {
  loginForm: FormGroup;

  constructor(private fb: FormBuilder, private http: HttpClient, private backendService: BackendService, private router: Router, private constantService: ConstantService) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      const { username, password } = this.loginForm.value;

      this.http
        .post(this.backendService.apiUrl+"/login", { username, password })
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
            console.log(localStorage.getItem('access_token'));

            this.constantService.setUser({
              "userid": response.user.id,
              "username": response.user.username,
              "organization": response.user.organization
            })
            this.router.navigate(['/project-list']); // Redirect to dashboard
            //alert('Login successful!');
          },
          error: (error) => {
            console.error('Error:', error);
            alert(error.error.detail || 'Login failed!');
          },
        });
    } else {
      console.log('Form is invalid');
    }
  }
}
