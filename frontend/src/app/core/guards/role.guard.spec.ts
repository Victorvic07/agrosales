import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
  UrlTree,
} from '@angular/router';
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import { AuthService } from '../auth/auth.service';
import { UserRole } from '../models/user-role';
import { roleGuard } from './role.guard';

describe('roleGuard', () => {
  const accessDeniedTree =
    {} as UrlTree;

  const authMock = {
    currentUser: vi.fn(),
  };

  const routerMock = {
    createUrlTree: vi.fn(),
  };

  beforeEach(() => {
    authMock.currentUser.mockReset();
    routerMock.createUrlTree.mockReset();

    routerMock.createUrlTree
      .mockReturnValue(
        accessDeniedTree,
      );

    TestBed.configureTestingModule({
      providers: [
        {
          provide: AuthService,
          useValue: authMock,
        },
        {
          provide: Router,
          useValue: routerMock,
        },
      ],
    });
  });

  it(
    'allows users with an accepted role',
    () => {
      authMock.currentUser
        .mockReturnValue({
          id: 'user-id',
          name: 'Administrador',
          email: 'admin@agrosales.com',
          role:
            UserRole.ADMINISTRADOR,
        });

      const route = {
        data: {
          roles: [
            UserRole.ADMINISTRADOR,
          ],
        },
      } as unknown as ActivatedRouteSnapshot;

      const result =
        TestBed.runInInjectionContext(
          () => roleGuard(route, {} as never),
        );

      expect(result).toBe(true);
    },
  );

  it(
    'redirects users without the required role',
    () => {
      authMock.currentUser
        .mockReturnValue({
          id: 'user-id',
          name: 'Vendedor',
          email:
            'vendedor@agrosales.com',
          role: UserRole.VENDEDOR,
        });

      const route = {
        data: {
          roles: [
            UserRole.ADMINISTRADOR,
          ],
        },
      } as unknown as ActivatedRouteSnapshot;

      const result =
        TestBed.runInInjectionContext(
          () => roleGuard(route, {} as never),
        );

      expect(result).toBe(
        accessDeniedTree,
      );

      expect(
        routerMock.createUrlTree,
      ).toHaveBeenCalledWith([
        '/access-denied',
      ]);
    },
  );
});