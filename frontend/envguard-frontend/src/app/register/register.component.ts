import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { BackendService } from '../backend.service';
import { HttpClient } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
  imports: [FormsModule, ReactiveFormsModule, CommonModule],
})

export class RegisterComponent {
  registerForm: FormGroup;

  constructor(private fb: FormBuilder, private backendService: BackendService, private http: HttpClient) {
    this.registerForm = this.fb.group(
      {
        username: ['', Validators.required],
        email: ['', [Validators.required, Validators.email]],
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
      const { username, email, password } = this.registerForm.value;

      this.http
        .post(this.backendService.apiUrl+"/register", { username, email, password })
        .pipe(
          catchError((error) => {
            console.error('Registration failed', error);
            return throwError(error);
          })
        )
        .subscribe({
          next: (response) => {
            console.log('Registration successful', response);
            alert('Registration successful!');
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

