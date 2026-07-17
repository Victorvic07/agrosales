import { inject } from '@angular/core';
import {
  CanActivateFn,
  Router,
} from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { UserRole } from '../models/user-role';

export const roleGuard: CanActivateFn = (
  route,
) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const currentUser =
    auth.currentUser();

  const allowedRoles =
    (route.data['roles'] as
      | UserRole[]
      | undefined) ?? [];

  if (
    currentUser &&
    allowedRoles.includes(
      currentUser.role,
    )
  ) {
    return true;
  }

  return router.createUrlTree([
    '/access-denied',
  ]);
};