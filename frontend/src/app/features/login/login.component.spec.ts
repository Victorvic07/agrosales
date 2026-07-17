import {
  Component,
} from '@angular/core';
import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import {
  provideRouter,
  Router,
} from '@angular/router';
import { of } from 'rxjs';
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { LoginComponent } from './login.component';

@Component({
  standalone: true,
  template: '<p>Dashboard</p>',
})
class DashboardTestComponent {}

describe('LoginComponent', () => {
  let fixture:
    ComponentFixture<LoginComponent>;

  const authMock = {
    login: vi.fn(),
  };

  beforeEach(async () => {
    authMock.login.mockReset();

    authMock.login.mockReturnValue(
      of({
        id: 'user-id',
        name: 'Usuário',
        email: 'user@agrosales.com',
        role: UserRole.VENDEDOR,
      }),
    );

    await TestBed
      .configureTestingModule({
        imports: [
          LoginComponent,
        ],
        providers: [
          provideRouter([
            {
              path: 'dashboard',
              component:
                DashboardTestComponent,
            },
          ]),
          {
            provide: AuthService,
            useValue: authMock,
          },
        ],
      })
      .compileComponents();

    fixture =
      TestBed.createComponent(
        LoginComponent,
      );

    fixture.detectChanges();
  });

  it(
    'does not submit an invalid form',
    () => {
      fixture.componentInstance.submit();

      expect(
        authMock.login,
      ).not.toHaveBeenCalled();

      expect(
        fixture.componentInstance
          .form.touched,
      ).toBe(true);
    },
  );

  it(
    'submits email, password and remember choice',
    () => {
      fixture.componentInstance
        .form.setValue({
          email:
            'user@agrosales.com',
          password: 'secret',
          remember: true,
        });

      fixture.componentInstance.submit();

      expect(
        authMock.login,
      ).toHaveBeenCalledWith(
        'user@agrosales.com',
        'secret',
        true,
      );
    },
  );

  it(
    'redirects to dashboard after login',
    () => {
      const router =
        TestBed.inject(Router);

      const navigateSpy =
        vi.spyOn(
          router,
          'navigateByUrl',
        );

      fixture.componentInstance
        .form.setValue({
          email:
            'user@agrosales.com',
          password: 'secret',
          remember: false,
        });

      fixture.componentInstance.submit();

      expect(
        navigateSpy,
      ).toHaveBeenCalledWith(
        '/dashboard',
      );
    },
  );

  it(
    'toggles password visibility',
    () => {
      expect(
        fixture.componentInstance
          .hidePassword(),
      ).toBe(true);

      fixture.componentInstance
        .togglePasswordVisibility();

      expect(
        fixture.componentInstance
          .hidePassword(),
      ).toBe(false);
    },
  );
});