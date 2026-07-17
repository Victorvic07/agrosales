import {
  HttpClient,
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import { AuthService } from '../auth/auth.service';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let httpClient: HttpClient;
  let httpTesting: HttpTestingController;

  const authMock = {
    accessToken: vi.fn(),
    logout: vi.fn(),
  };

  const routerMock = {
    url: '/products',
    navigate: vi.fn(),
  };

  beforeEach(() => {
    authMock.accessToken.mockReset();
    authMock.logout.mockReset();
    routerMock.navigate.mockReset();

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(
          withInterceptors([
            authInterceptor,
          ]),
        ),
        provideHttpClientTesting(),
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

    httpClient =
      TestBed.inject(HttpClient);

    httpTesting =
      TestBed.inject(
        HttpTestingController,
      );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('adds the bearer token', () => {
    authMock.accessToken.mockReturnValue(
      'token',
    );

    httpClient
      .get('/api/v1/products')
      .subscribe();

    const request = httpTesting.expectOne(
      '/api/v1/products',
    );

    expect(
      request.request.headers.get(
        'Authorization',
      ),
    ).toBe('Bearer token');

    request.flush([]);
  });

  it(
    'does not add the token to login',
    () => {
      authMock.accessToken.mockReturnValue(
        'token',
      );

      httpClient
        .post('/api/v1/auth/login', {})
        .subscribe();

      const request =
        httpTesting.expectOne(
          '/api/v1/auth/login',
        );

      expect(
        request.request.headers.has(
          'Authorization',
        ),
      ).toBe(false);

      request.flush({});
    },
  );

  it(
    'logs out and redirects on 401',
    () => {
      authMock.accessToken.mockReturnValue(
        'token',
      );

      httpClient
        .get('/api/v1/products')
        .subscribe({
          error: () => undefined,
        });

      const request =
        httpTesting.expectOne(
          '/api/v1/products',
        );

      request.flush(
        {},
        {
          status: 401,
          statusText: 'Unauthorized',
        },
      );

      expect(
        authMock.logout,
      ).toHaveBeenCalledOnce();

      expect(
        routerMock.navigate,
      ).toHaveBeenCalledWith(
        ['/login'],
        {
          queryParams: {
            returnUrl: '/products',
          },
        },
      );
    },
  );

  it('redirects on 403', () => {
    authMock.accessToken.mockReturnValue(
      'token',
    );

    httpClient
      .get('/api/v1/users')
      .subscribe({
        error: () => undefined,
      });

    const request =
      httpTesting.expectOne(
        '/api/v1/users',
      );

    request.flush(
      {},
      {
        status: 403,
        statusText: 'Forbidden',
      },
    );

    expect(
      routerMock.navigate,
    ).toHaveBeenCalledWith([
      '/access-denied',
    ]);
  });
});