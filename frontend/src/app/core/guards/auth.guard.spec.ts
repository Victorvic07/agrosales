import { TestBed } from '@angular/core/testing';
import {
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
import { authGuard } from './auth.guard';

describe('authGuard', () => {
  const authMock = {
    isAuthenticated: vi.fn(),
  };

  const loginTree =
    {} as UrlTree;

  const routerMock = {
    createUrlTree: vi.fn(),
  };

  beforeEach(() => {
    authMock.isAuthenticated.mockReset();
    routerMock.createUrlTree.mockReset();

    routerMock.createUrlTree.mockReturnValue(
      loginTree,
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
    'allows authenticated users',
    () => {
      authMock.isAuthenticated
        .mockReturnValue(true);

      const result =
        TestBed.runInInjectionContext(
          () =>
            authGuard(
              {} as never,
              {
                url: '/orders',
              } as never,
            ),
        );

      expect(result).toBe(true);

      expect(
        routerMock.createUrlTree,
      ).not.toHaveBeenCalled();
    },
  );

  it(
    'redirects anonymous users to login',
    () => {
      authMock.isAuthenticated
        .mockReturnValue(false);

      const result =
        TestBed.runInInjectionContext(
          () =>
            authGuard(
              {} as never,
              {
                url: '/orders',
              } as never,
            ),
        );

      expect(result).toBe(loginTree);

      expect(
        routerMock.createUrlTree,
      ).toHaveBeenCalledWith(
        ['/login'],
        {
          queryParams: {
            returnUrl: '/orders',
          },
        },
      );
    },
  );
});