import { HttpErrorResponse } from '@angular/common/http';
import { Component, signal } from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  readonly loading = signal(false);
  readonly hidePassword = signal(true);
  readonly errorMessage = signal<string | null>(null);

  readonly form = new FormGroup({
    email: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.email,
      ],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [
        Validators.required,
      ],
    }),
    remember: new FormControl(false, {
      nonNullable: true,
    }),
  });

  constructor(
    private readonly auth: AuthService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  togglePasswordVisibility(): void {
    this.hidePassword.update(
      (currentValue) => !currentValue,
    );
  }

  submit(): void {
    if (
      this.form.invalid ||
      this.loading()
    ) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    const {
      email,
      password,
      remember,
    } = this.form.getRawValue();

    this.auth
      .login(
        email,
        password,
        remember,
      )
      .pipe(
        finalize(() => {
          this.loading.set(false);
        }),
      )
      .subscribe({
        next: () => {
          const returnUrl =
            this.route.snapshot.queryParamMap.get(
              'returnUrl',
            );

          void this.router.navigateByUrl(
            returnUrl?.startsWith('/')
              ? returnUrl
              : '/dashboard',
          );
        },
        error: (
          error: HttpErrorResponse,
        ) => {
          this.errorMessage.set(
            this.resolveErrorMessage(error),
          );
        },
      });
  }

  private resolveErrorMessage(
    error: HttpErrorResponse,
  ): string {
    if (error.status === 401) {
      return 'E-mail ou senha inválidos.';
    }

    if (error.status === 403) {
      return 'Este usuário não possui permissão para acessar o sistema.';
    }

    if (error.status === 0) {
      return 'Não foi possível conectar com a API do AgroSales.';
    }

    return 'Não foi possível entrar no AgroSales. Tente novamente.';
  }
}