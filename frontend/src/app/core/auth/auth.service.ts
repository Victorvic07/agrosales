import {
  HttpClient,
  HttpHeaders,
} from '@angular/common/http';
import {
  computed,
  Injectable,
  signal,
} from '@angular/core';
import {
  Observable,
  switchMap,
  tap,
} from 'rxjs';

import {
  AuthUser,
  LoginResponse,
  StoredSession,
} from '../models/auth.models';
import { AuthStorageService } from './auth-storage.service';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly session =
    signal<StoredSession | null>(null);

  readonly currentUser = computed(
    () => this.session()?.user ?? null,
  );

  readonly isAuthenticated = computed(
    () => this.session() !== null,
  );

  constructor(
    private readonly http: HttpClient,
    private readonly storage: AuthStorageService,
  ) {
    this.session.set(this.storage.read());
  }

  accessToken(): string | null {
    return this.session()?.accessToken ?? null;
  }

  login(
    email: string,
    password: string,
    remember: boolean,
  ): Observable<AuthUser> {
    const body = new URLSearchParams();

    body.set('username', email);
    body.set('password', password);

    return this.http
      .post<LoginResponse>(
        '/api/v1/auth/login',
        body.toString(),
        {
          headers: new HttpHeaders({
            'Content-Type':
              'application/x-www-form-urlencoded',
          }),
        },
      )
      .pipe(
        switchMap((loginResponse) =>
          this.http
            .get<AuthUser>(
              '/api/v1/auth/me',
              {
                headers: new HttpHeaders({
                  Authorization:
                    `Bearer ${loginResponse.access_token}`,
                }),
              },
            )
            .pipe(
              tap((user) => {
                const session: StoredSession = {
                  accessToken:
                    loginResponse.access_token,
                  user,
                };

                this.storage.save(
                  session,
                  remember,
                );

                this.session.set(session);
              }),
            ),
        ),
      );
  }

  logout(): void {
    this.storage.clear();
    this.session.set(null);
  }
}