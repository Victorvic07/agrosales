import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import {
  StoredSession,
} from '../models/auth.models';
import { UserRole } from '../models/user-role';
import { AuthStorageService } from './auth-storage.service';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let http: HttpTestingController;

  const storageMock = {
    save: vi.fn(),
    read: vi.fn(),
    clear: vi.fn(),
  };

  function configureService(
    storedSession: StoredSession | null = null,
  ): AuthService {
    storageMock.read.mockReturnValue(
      storedSession,
    );

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: AuthStorageService,
          useValue: storageMock,
        },
      ],
    });

    http = TestBed.inject(
      HttpTestingController,
    );

    return TestBed.inject(AuthService);
  }

  beforeEach(() => {
    TestBed.resetTestingModule();

    storageMock.save.mockReset();
    storageMock.read.mockReset();
    storageMock.clear.mockReset();
  });

  afterEach(() => {
    http?.verify();
  });

  it(
    'logs in, loads the current user and stores the session',
    () => {
      const service = configureService();

      service
        .login(
          'user@agrosales.com',
          'secret',
          true,
        )
        .subscribe();

      const loginRequest = http.expectOne(
        '/api/v1/auth/login',
      );

      expect(
        loginRequest.request.method,
      ).toBe('POST');

      expect(
        loginRequest.request.headers.get(
          'Content-Type',
        ),
      ).toBe(
        'application/x-www-form-urlencoded',
      );

      loginRequest.flush({
        access_token: 'token',
        token_type: 'bearer',
      });

      const meRequest = http.expectOne(
        '/api/v1/users/me',
      );

      expect(
        meRequest.request.method,
      ).toBe('GET');

      expect(
        meRequest.request.headers.get(
          'Authorization',
        ),
      ).toBe('Bearer token');

      meRequest.flush({
        id: 'user-id',
        name: 'Usuário',
        email: 'user@agrosales.com',
        role: UserRole.VENDEDOR,
      });

      expect(
        storageMock.save,
      ).toHaveBeenCalledWith(
        {
          accessToken: 'token',
          user: {
            id: 'user-id',
            name: 'Usuário',
            email: 'user@agrosales.com',
            role: UserRole.VENDEDOR,
          },
        },
        true,
      );

      expect(
        service.isAuthenticated(),
      ).toBe(true);

      expect(
        service.accessToken(),
      ).toBe('token');
    },
  );

  it(
    'loads the stored session on startup',
    () => {
      const service = configureService({
        accessToken: 'stored-token',
        user: {
          id: 'stored-user',
          name: 'Usuário salvo',
          email: 'stored@agrosales.com',
          role: UserRole.PRODUTOR,
        },
      });

      expect(
        service.isAuthenticated(),
      ).toBe(true);

      expect(
        service.currentUser()?.role,
      ).toBe(UserRole.PRODUTOR);

      expect(
        service.accessToken(),
      ).toBe('stored-token');
    },
  );

  it('clears the session on logout', () => {
    const service = configureService({
      accessToken: 'token',
      user: {
        id: 'user-id',
        name: 'Usuário',
        email: 'user@agrosales.com',
        role: UserRole.VENDEDOR,
      },
    });

    service.logout();

    expect(
      storageMock.clear,
    ).toHaveBeenCalledOnce();

    expect(
      service.currentUser(),
    ).toBeNull();

    expect(
      service.isAuthenticated(),
    ).toBe(false);

    expect(
      service.accessToken(),
    ).toBeNull();
  });
});