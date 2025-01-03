import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { BackendService } from '../backend.service';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { routes } from '../app.routes';
import { Router } from '@angular/router';
import { ConstantService } from '../constant.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
  imports: [FormsModule, ReactiveFormsModule, CommonModule],
})

export class RegisterComponent {
  registerForm: FormGroup;

  constructor(private fb: FormBuilder, private backendService: BackendService, private http: HttpClient, private router: Router, private constantService: ConstantService) {
    this.registerForm = this.fb.group(
      {
        username: ['', Validators.required],
        organization: ['', [Validators.required, Validators.minLength(2)]],
        password: ['', [Validators.required, Validators.minLength(6)]],
        confirmPassword: ['', Validators.required],
      },
      { validator: this.passwordMatchValidator }
    );
  }

  passwordMatchValidator(form: FormGroup) {
    const password = form.get('password')?.value;
    const confirmPassword = form.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { mismatch: true };
  }

  onSubmit() {
    if (this.registerForm.valid) {
      const { username, organization, password } = this.registerForm.value;

      this.http
        .post(this.backendService.apiUrl+"/register", { username, organization, password })
        .pipe(
          catchError((error) => {
            console.error('Registration failed', error);
            //alert(error.message);
            return throwError(error);
          })
        )
        .subscribe({
          next: (response: any) => {
            console.log('Registration successful', response);
            //alert('Registration successful!');
            this.constantService.setUser({
              "userid": response.id,
              "username": response.username,
              "organization": response.organization
            })
            this.router.navigate(["project-list"]); //dashboard
          },
          error: (error) => {
            console.error('Error:', error);
            alert(error.error.detail || 'Registration failed!');
          },
        });
    } else {
      console.log('Form is invalid');
    }
  }
}

