import {
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import {
  catchError,
  throwError,
} from 'rxjs';

import { AuthService } from '../auth/auth.service';

export const authInterceptor: HttpInterceptorFn = (
  request,
  next,
) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const token = auth.accessToken();

  const isLoginRequest =
    request.url.includes('/api/v1/auth/login');

  const authenticatedRequest =
    token && !isLoginRequest
      ? request.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`,
          },
        })
      : request;

  return next(authenticatedRequest).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        auth.logout();

        void router.navigate(['/login'], {
          queryParams: {
            returnUrl: router.url,
          },
        });
      }

      if (error.status === 403) {
        void router.navigate([
          '/access-denied',
        ]);
      }

      return throwError(() => error);
    }),
  );
};