# AgroSales Frontend Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar do zero o frontend Angular do AgroSales com login real, sessão persistente, layout responsivo, menu por perfil, rotas protegidas, páginas 403/404 e páginas-base dos módulos.

**Architecture:** Aplicação Angular standalone com divisão entre `core`, `layout`, `features` e `shared`. O `AuthService` será a única fonte da sessão, o interceptor adicionará o Bearer token e os guards controlarão autenticação e perfil. O shell autenticado usará Angular Material com sidenav recolhível no desktop e drawer sobreposto no celular.

**Tech Stack:** Angular standalone, Angular Material, Angular Router, HttpClient, Reactive Forms, TypeScript, SCSS e testes unitários do Angular.

## Global Constraints

- Projeto frontend criado em `C:\Projetos\agrosales\frontend`.
- Componentes standalone.
- Angular Material como biblioteca visual.
- SCSS como formato de estilos.
- Paleta: verde, branco e detalhes em laranja.
- Layout responsivo para desktop, tablet e celular.
- Menu: Dashboard, Produtos, Variações, Lotes, Clientes, Pedidos, Usuários e Sair.
- Administrador vê todos os módulos.
- Produtor não vê Usuários.
- Vendedor vê Dashboard, Produtos, Clientes e Pedidos.
- “Lembrar de mim” usa `localStorage`; sessão temporária usa `sessionStorage`.
- Login redireciona para a rota protegida anterior quando válida; caso contrário, `/dashboard`.
- `401` encerra a sessão; `403` direciona para `/access-denied`.
- Nenhum CRUD completo de negócio faz parte deste plano.

---

## File Map

### Arquivos de configuração

- Create: `frontend/proxy.conf.json` — proxy local para a API.
- Modify: `frontend/src/styles.scss` — tema global e tokens visuais.
- Modify: `frontend/src/app/app.config.ts` — providers de Router, HttpClient e interceptor.
- Modify: `frontend/src/app/app.routes.ts` — árvore completa de rotas.

### Core

- Create: `frontend/src/app/core/models/user-role.ts`
- Create: `frontend/src/app/core/models/auth.models.ts`
- Create: `frontend/src/app/core/auth/auth-storage.service.ts`
- Create: `frontend/src/app/core/auth/auth.service.ts`
- Create: `frontend/src/app/core/auth/auth.service.spec.ts`
- Create: `frontend/src/app/core/interceptors/auth.interceptor.ts`
- Create: `frontend/src/app/core/interceptors/auth.interceptor.spec.ts`
- Create: `frontend/src/app/core/guards/auth.guard.ts`
- Create: `frontend/src/app/core/guards/auth.guard.spec.ts`
- Create: `frontend/src/app/core/guards/role.guard.ts`
- Create: `frontend/src/app/core/guards/role.guard.spec.ts`

### Shared

- Create: `frontend/src/app/shared/navigation/navigation-item.ts`
- Create: `frontend/src/app/shared/navigation/navigation.config.ts`

### Layout

- Create: `frontend/src/app/layout/app-shell/app-shell.component.ts`
- Create: `frontend/src/app/layout/app-shell/app-shell.component.html`
- Create: `frontend/src/app/layout/app-shell/app-shell.component.scss`
- Create: `frontend/src/app/layout/sidebar/sidebar.component.ts`
- Create: `frontend/src/app/layout/sidebar/sidebar.component.html`
- Create: `frontend/src/app/layout/sidebar/sidebar.component.scss`
- Create: `frontend/src/app/layout/sidebar/sidebar.component.spec.ts`
- Create: `frontend/src/app/layout/topbar/topbar.component.ts`
- Create: `frontend/src/app/layout/topbar/topbar.component.html`
- Create: `frontend/src/app/layout/topbar/topbar.component.scss`

### Features

- Create: `frontend/src/app/features/login/login.component.ts`
- Create: `frontend/src/app/features/login/login.component.html`
- Create: `frontend/src/app/features/login/login.component.scss`
- Create: `frontend/src/app/features/login/login.component.spec.ts`
- Create: `frontend/src/app/features/access-denied/access-denied.component.ts`
- Create: `frontend/src/app/features/not-found/not-found.component.ts`
- Create: `frontend/src/app/features/placeholder/feature-placeholder.component.ts`
- Create: `frontend/src/app/features/placeholder/feature-placeholder.component.html`
- Create: `frontend/src/app/features/placeholder/feature-placeholder.component.scss`

---

### Task 1: Scaffold Angular and Material

**Files:**
- Create: `frontend/`
- Create: `frontend/proxy.conf.json`
- Modify: `frontend/package.json`

**Interfaces:**
- Consumes: Backend disponível em `http://192.168.100.30:8000`.
- Produces: Aplicação Angular standalone executável por `npm start`.

- [ ] **Step 1: Create the Angular project**

No **PC principal**, execute:

```powershell
cd "C:\Projetos\agrosales"

npx @angular/cli new frontend `
  --standalone `
  --routing `
  --style=scss `
  --skip-git `
  --package-manager=npm
```

Expected: pasta `C:\Projetos\agrosales\frontend` criada.

- [ ] **Step 2: Add Angular Material**

```powershell
cd "C:\Projetos\agrosales\frontend"

npx ng add @angular/material
```

Selecione:

```text
Theme: Custom
Typography: Yes
Animations: Include and enable
```

- [ ] **Step 3: Create the development proxy**

```powershell
New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\proxy.conf.json"
```

Conteúdo:

```json
{
  "/api": {
    "target": "http://192.168.100.30:8000",
    "secure": false,
    "changeOrigin": true
  }
}
```

- [ ] **Step 4: Update the start script**

Em `frontend/package.json`, altere:

```json
"start": "ng serve --proxy-config proxy.conf.json"
```

- [ ] **Step 5: Verify scaffold**

```powershell
npm test -- --watch=false
npm run build
```

Expected: ambos terminam com exit code `0`.

- [ ] **Step 6: Commit**

```powershell
cd "C:\Projetos\agrosales"

git add frontend
git commit -m "chore: cria frontend Angular com Material"
```

---

### Task 2: Define authentication models and storage

**Files:**
- Create: `frontend/src/app/core/models/user-role.ts`
- Create: `frontend/src/app/core/models/auth.models.ts`
- Create: `frontend/src/app/core/auth/auth-storage.service.ts`
- Test: `frontend/src/app/core/auth/auth-storage.service.spec.ts`

**Interfaces:**
- Produces:
  - `UserRole`
  - `AuthUser`
  - `LoginRequest`
  - `LoginResponse`
  - `StoredSession`
  - `AuthStorageService.save(session, remember)`
  - `AuthStorageService.read()`
  - `AuthStorageService.clear()`

- [ ] **Step 1: Create directories and files**

```powershell
cd "C:\Projetos\agrosales\frontend"

New-Item -ItemType Directory -Force `
  "src\app\core\models", `
  "src\app\core\auth"

New-Item -ItemType File -Force `
  "src\app\core\models\user-role.ts", `
  "src\app\core\models\auth.models.ts", `
  "src\app\core\auth\auth-storage.service.ts", `
  "src\app\core\auth\auth-storage.service.spec.ts"
```

- [ ] **Step 2: Write the failing storage tests**

`auth-storage.service.spec.ts`:

```typescript
import { TestBed } from '@angular/core/testing';

import { AuthStorageService } from './auth-storage.service';
import { StoredSession } from '../models/auth.models';
import { UserRole } from '../models/user-role';

describe('AuthStorageService', () => {
  let service: AuthStorageService;

  const session: StoredSession = {
    accessToken: 'token',
    user: {
      id: 'user-id',
      name: 'Usuário',
      email: 'user@agrosales.com',
      role: UserRole.VENDEDOR,
    },
  };

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();

    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthStorageService);
  });

  it('stores remembered sessions in localStorage', () => {
    service.save(session, true);

    expect(localStorage.getItem('agrosales.session')).not.toBeNull();
    expect(sessionStorage.getItem('agrosales.session')).toBeNull();
  });

  it('stores temporary sessions in sessionStorage', () => {
    service.save(session, false);

    expect(sessionStorage.getItem('agrosales.session')).not.toBeNull();
    expect(localStorage.getItem('agrosales.session')).toBeNull();
  });

  it('clears both storages', () => {
    service.save(session, true);
    service.clear();

    expect(service.read()).toBeNull();
  });
});
```

- [ ] **Step 3: Run tests and verify failure**

```powershell
npm test -- --watch=false --include="src/app/core/auth/auth-storage.service.spec.ts"
```

Expected: FAIL porque tipos e serviço ainda não existem.

- [ ] **Step 4: Implement models**

`user-role.ts`:

```typescript
export enum UserRole {
  ADMINISTRADOR = 'ADMINISTRADOR',
  PRODUTOR = 'PRODUTOR',
  VENDEDOR = 'VENDEDOR',
}
```

`auth.models.ts`:

```typescript
import { UserRole } from './user-role';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}

export interface StoredSession {
  accessToken: string;
  user: AuthUser;
}
```

- [ ] **Step 5: Implement storage service**

`auth-storage.service.ts`:

```typescript
import { Injectable } from '@angular/core';

import { StoredSession } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class AuthStorageService {
  private readonly key = 'agrosales.session';

  save(session: StoredSession, remember: boolean): void {
    this.clear();

    const storage = remember ? localStorage : sessionStorage;
    storage.setItem(this.key, JSON.stringify(session));
  }

  read(): StoredSession | null {
    const raw =
      localStorage.getItem(this.key) ??
      sessionStorage.getItem(this.key);

    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as StoredSession;
    } catch {
      this.clear();
      return null;
    }
  }

  clear(): void {
    localStorage.removeItem(this.key);
    sessionStorage.removeItem(this.key);
  }
}
```

- [ ] **Step 6: Run tests and verify pass**

```powershell
npm test -- --watch=false --include="src/app/core/auth/auth-storage.service.spec.ts"
```

Expected: `3 specs, 0 failures`.

- [ ] **Step 7: Commit**

```powershell
git add frontend/src/app/core
git commit -m "feat: adiciona modelos e armazenamento de sessão"
```

---

### Task 3: Implement AuthService with real API

**Files:**
- Create: `frontend/src/app/core/auth/auth.service.ts`
- Create: `frontend/src/app/core/auth/auth.service.spec.ts`

**Interfaces:**
- Consumes:
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
  - `AuthStorageService`
- Produces:
  - `currentUser: Signal<AuthUser | null>`
  - `isAuthenticated: Signal<boolean>`
  - `accessToken(): string | null`
  - `login(email, password, remember): Observable<AuthUser>`
  - `logout(): void`

- [ ] **Step 1: Create files**

```powershell
New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\src\app\core\auth\auth.service.ts", `
  "C:\Projetos\agrosales\frontend\src\app\core\auth\auth.service.spec.ts"
```

- [ ] **Step 2: Write failing tests**

`auth.service.spec.ts`:

```typescript
import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthService } from './auth.service';
import { AuthStorageService } from './auth-storage.service';
import { UserRole } from '../models/user-role';

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;
  let storage: jasmine.SpyObj<AuthStorageService>;

  beforeEach(() => {
    storage = jasmine.createSpyObj<AuthStorageService>(
      'AuthStorageService',
      ['save', 'read', 'clear'],
    );
    storage.read.and.returnValue(null);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AuthStorageService, useValue: storage },
        {
          provide: Router,
          useValue: jasmine.createSpyObj('Router', ['navigateByUrl']),
        },
      ],
    });

    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('logs in, loads the current user and stores the session', () => {
    service.login('user@agrosales.com', 'secret', true).subscribe();

    http.expectOne('/api/v1/auth/login').flush({
      access_token: 'token',
      token_type: 'bearer',
    });

    http.expectOne('/api/v1/auth/me').flush({
      id: 'user-id',
      name: 'Usuário',
      email: 'user@agrosales.com',
      role: UserRole.VENDEDOR,
    });

    expect(storage.save).toHaveBeenCalledWith(
      jasmine.objectContaining({ accessToken: 'token' }),
      true,
    );
    expect(service.isAuthenticated()).toBeTrue();
  });

  it('clears the session on logout', () => {
    service.logout();

    expect(storage.clear).toHaveBeenCalled();
    expect(service.currentUser()).toBeNull();
  });
});
```

- [ ] **Step 3: Run test and verify failure**

```powershell
npm test -- --watch=false --include="src/app/core/auth/auth.service.spec.ts"
```

Expected: FAIL porque `AuthService` ainda não existe.

- [ ] **Step 4: Implement AuthService**

`auth.service.ts`:

```typescript
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  computed,
  Injectable,
  signal,
} from '@angular/core';
import { Observable, switchMap, tap } from 'rxjs';

import {
  AuthUser,
  LoginResponse,
  StoredSession,
} from '../models/auth.models';
import { AuthStorageService } from './auth-storage.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly session = signal<StoredSession | null>(
    this.storage.read(),
  );

  readonly currentUser = computed(
    () => this.session()?.user ?? null,
  );

  readonly isAuthenticated = computed(
    () => this.session() !== null,
  );

  constructor(
    private readonly http: HttpClient,
    private readonly storage: AuthStorageService,
  ) {}

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
            .get<AuthUser>('/api/v1/auth/me', {
              headers: new HttpHeaders({
                Authorization:
                  `Bearer ${loginResponse.access_token}`,
              }),
            })
            .pipe(
              tap((user) => {
                const session: StoredSession = {
                  accessToken: loginResponse.access_token,
                  user,
                };

                this.storage.save(session, remember);
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
```

- [ ] **Step 5: Verify tests**

```powershell
npm test -- --watch=false --include="src/app/core/auth/auth.service.spec.ts"
```

Expected: `2 specs, 0 failures`.

- [ ] **Step 6: Commit**

```powershell
git add frontend/src/app/core/auth
git commit -m "feat: implementa autenticação com API"
```

---

### Task 4: Add HTTP interceptor

**Files:**
- Create: `frontend/src/app/core/interceptors/auth.interceptor.ts`
- Create: `frontend/src/app/core/interceptors/auth.interceptor.spec.ts`
- Modify: `frontend/src/app/app.config.ts`

**Interfaces:**
- Consumes: `AuthService.accessToken()` e `AuthService.logout()`.
- Produces: `authInterceptor`.

- [ ] **Step 1: Create files**

```powershell
New-Item -ItemType Directory -Force `
  "C:\Projetos\agrosales\frontend\src\app\core\interceptors"

New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\src\app\core\interceptors\auth.interceptor.ts", `
  "C:\Projetos\agrosales\frontend\src\app\core\interceptors\auth.interceptor.spec.ts"
```

- [ ] **Step 2: Write failing interceptor tests**

```typescript
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

import { AuthService } from '../auth/auth.service';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let httpClient: HttpClient;
  let httpTesting: HttpTestingController;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    auth = jasmine.createSpyObj<AuthService>(
      'AuthService',
      ['accessToken', 'logout'],
    );
    router = jasmine.createSpyObj<Router>(
      'Router',
      ['navigate'],
    );

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: auth },
        { provide: Router, useValue: router },
      ],
    });

    httpClient = TestBed.inject(HttpClient);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  it('adds the bearer token', () => {
    auth.accessToken.and.returnValue('token');

    httpClient.get('/api/v1/products').subscribe();

    const request = httpTesting.expectOne('/api/v1/products');
    expect(
      request.request.headers.get('Authorization'),
    ).toBe('Bearer token');

    request.flush([]);
  });

  it('logs out and redirects on 401', () => {
    auth.accessToken.and.returnValue('token');

    httpClient.get('/api/v1/products').subscribe({
      error: () => undefined,
    });

    const request = httpTesting.expectOne('/api/v1/products');
    request.flush({}, { status: 401, statusText: 'Unauthorized' });

    expect(auth.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(
      ['/login'],
      jasmine.any(Object),
    );
  });
});
```

- [ ] **Step 3: Run and verify failure**

```powershell
npm test -- --watch=false --include="src/app/core/interceptors/auth.interceptor.spec.ts"
```

Expected: FAIL porque interceptor não existe.

- [ ] **Step 4: Implement interceptor**

```typescript
import {
  HttpErrorResponse,
  HttpInterceptorFn,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

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
        void router.navigate(['/access-denied']);
      }

      return throwError(() => error);
    }),
  );
};
```

- [ ] **Step 5: Register interceptor**

Em `app.config.ts`, configure:

```typescript
import {
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';

import { authInterceptor } from './core/interceptors/auth.interceptor';

provideHttpClient(
  withInterceptors([authInterceptor]),
),
```

- [ ] **Step 6: Verify tests and build**

```powershell
npm test -- --watch=false --include="src/app/core/interceptors/auth.interceptor.spec.ts"
npm run build
```

Expected: testes e build passam.

- [ ] **Step 7: Commit**

```powershell
git add frontend/src/app/core/interceptors frontend/src/app/app.config.ts
git commit -m "feat: adiciona interceptor de autenticação"
```

---

### Task 5: Add authentication and role guards

**Files:**
- Create: `frontend/src/app/core/guards/auth.guard.ts`
- Create: `frontend/src/app/core/guards/auth.guard.spec.ts`
- Create: `frontend/src/app/core/guards/role.guard.ts`
- Create: `frontend/src/app/core/guards/role.guard.spec.ts`

**Interfaces:**
- Produces:
  - `authGuard: CanActivateFn`
  - `roleGuard: CanActivateFn`
- Route role data shape: `{ roles: UserRole[] }`.

- [ ] **Step 1: Create files**

```powershell
New-Item -ItemType Directory -Force `
  "C:\Projetos\agrosales\frontend\src\app\core\guards"

New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\src\app\core\guards\auth.guard.ts", `
  "C:\Projetos\agrosales\frontend\src\app\core\guards\auth.guard.spec.ts", `
  "C:\Projetos\agrosales\frontend\src\app\core\guards\role.guard.ts", `
  "C:\Projetos\agrosales\frontend\src\app\core\guards\role.guard.spec.ts"
```

- [ ] **Step 2: Write failing auth guard test**

```typescript
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { authGuard } from './auth.guard';

describe('authGuard', () => {
  it('returns a login UrlTree for anonymous users', () => {
    const router = jasmine.createSpyObj<Router>(
      'Router',
      ['createUrlTree'],
    );
    const tree = {} as ReturnType<Router['createUrlTree']>;
    router.createUrlTree.and.returnValue(tree);

    TestBed.configureTestingModule({
      providers: [
        {
          provide: AuthService,
          useValue: { isAuthenticated: () => false },
        },
        { provide: Router, useValue: router },
      ],
    });

    const result = TestBed.runInInjectionContext(() =>
      authGuard(
        {} as never,
        { url: '/orders' } as never,
      ),
    );

    expect(result).toBe(tree);
    expect(router.createUrlTree).toHaveBeenCalledWith(
      ['/login'],
      { queryParams: { returnUrl: '/orders' } },
    );
  });
});
```

- [ ] **Step 3: Write failing role guard test**

```typescript
import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  Router,
} from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { UserRole } from '../models/user-role';
import { roleGuard } from './role.guard';

describe('roleGuard', () => {
  it('redirects users without the required role', () => {
    const router = jasmine.createSpyObj<Router>(
      'Router',
      ['createUrlTree'],
    );
    const tree = {} as ReturnType<Router['createUrlTree']>;
    router.createUrlTree.and.returnValue(tree);

    const route = {
      data: {
        roles: [UserRole.ADMINISTRADOR],
      },
    } as unknown as ActivatedRouteSnapshot;

    TestBed.configureTestingModule({
      providers: [
        {
          provide: AuthService,
          useValue: {
            currentUser: () => ({
              role: UserRole.VENDEDOR,
            }),
          },
        },
        { provide: Router, useValue: router },
      ],
    });

    const result = TestBed.runInInjectionContext(() =>
      roleGuard(route),
    );

    expect(result).toBe(tree);
  });
});
```

- [ ] **Step 4: Run tests and verify failure**

```powershell
npm test -- --watch=false --include="src/app/core/guards/*.spec.ts"
```

Expected: FAIL porque guards não existem.

- [ ] **Step 5: Implement auth guard**

```typescript
import { inject } from '@angular/core';
import {
  CanActivateFn,
  Router,
} from '@angular/router';

import { AuthService } from '../auth/auth.service';

export const authGuard: CanActivateFn = (
  _route,
  state,
) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login'], {
    queryParams: {
      returnUrl: state.url,
    },
  });
};
```

- [ ] **Step 6: Implement role guard**

```typescript
import { inject } from '@angular/core';
import {
  CanActivateFn,
  Router,
} from '@angular/router';

import { AuthService } from '../auth/auth.service';
import { UserRole } from '../models/user-role';

export const roleGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const currentUser = auth.currentUser();
  const allowedRoles =
    (route.data['roles'] as UserRole[] | undefined) ?? [];

  if (
    currentUser &&
    allowedRoles.includes(currentUser.role)
  ) {
    return true;
  }

  return router.createUrlTree(['/access-denied']);
};
```

- [ ] **Step 7: Verify tests**

```powershell
npm test -- --watch=false --include="src/app/core/guards/*.spec.ts"
```

Expected: todos os testes passam.

- [ ] **Step 8: Commit**

```powershell
git add frontend/src/app/core/guards
git commit -m "feat: protege rotas por autenticação e perfil"
```

---

### Task 6: Build login screen

**Files:**
- Create: `frontend/src/app/features/login/login.component.ts`
- Create: `frontend/src/app/features/login/login.component.html`
- Create: `frontend/src/app/features/login/login.component.scss`
- Create: `frontend/src/app/features/login/login.component.spec.ts`

**Interfaces:**
- Consumes: `AuthService.login()`, query param `returnUrl`.
- Produces: rota `/login`.

- [ ] **Step 1: Create files**

```powershell
New-Item -ItemType Directory -Force `
  "C:\Projetos\agrosales\frontend\src\app\features\login"

New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\src\app\features\login\login.component.ts", `
  "C:\Projetos\agrosales\frontend\src\app\features\login\login.component.html", `
  "C:\Projetos\agrosales\frontend\src\app\features\login\login.component.scss", `
  "C:\Projetos\agrosales\frontend\src\app\features\login\login.component.spec.ts"
```

- [ ] **Step 2: Write failing component test**

```typescript
import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let auth: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    auth = jasmine.createSpyObj<AuthService>(
      'AuthService',
      ['login'],
    );
    auth.login.and.returnValue(
      of({
        id: '1',
        name: 'Usuário',
        email: 'user@agrosales.com',
        role: UserRole.VENDEDOR,
      }),
    );

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideHttpClient(),
        provideRouter([]),
        { provide: AuthService, useValue: auth },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();
  });

  it('does not submit an invalid form', () => {
    fixture.componentInstance.submit();

    expect(auth.login).not.toHaveBeenCalled();
  });

  it('submits email, password and remember choice', () => {
    fixture.componentInstance.form.setValue({
      email: 'user@agrosales.com',
      password: 'secret',
      remember: true,
    });

    fixture.componentInstance.submit();

    expect(auth.login).toHaveBeenCalledWith(
      'user@agrosales.com',
      'secret',
      true,
    );
  });
});
```

- [ ] **Step 3: Run test and verify failure**

```powershell
npm test -- --watch=false --include="src/app/features/login/login.component.spec.ts"
```

Expected: FAIL porque componente não existe.

- [ ] **Step 4: Implement component logic**

`login.component.ts`:

```typescript
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
import {
  ActivatedRoute,
  Router,
} from '@angular/router';
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
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
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

  submit(): void {
    if (this.form.invalid || this.loading()) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    const { email, password, remember } =
      this.form.getRawValue();

    this.auth
      .login(email, password, remember)
      .pipe(finalize(() => this.loading.set(false)))
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
        error: (error: HttpErrorResponse) => {
          this.errorMessage.set(
            error.status === 401
              ? 'E-mail ou senha inválidos.'
              : 'Não foi possível acessar o AgroSales.',
          );
        },
      });
  }
}
```

- [ ] **Step 5: Implement login template**

`login.component.html`:

```html
<main class="login-page">
  <section class="brand-panel">
    <div class="brand-content">
      <span class="brand-mark">AgroSales</span>
      <h1>Gestão agrícola e comercial em um só lugar.</h1>
      <p>
        Controle produtos, estoque, clientes e pedidos com
        clareza e agilidade.
      </p>
    </div>
  </section>

  <section class="form-panel">
    <form [formGroup]="form" (ngSubmit)="submit()">
      <header>
        <span class="eyebrow">Bem-vindo</span>
        <h2>Entre na sua conta</h2>
        <p>Use suas credenciais do AgroSales.</p>
      </header>

      <mat-form-field appearance="outline">
        <mat-label>E-mail</mat-label>
        <input
          matInput
          type="email"
          formControlName="email"
          autocomplete="username"
        />
        <mat-icon matSuffix>mail</mat-icon>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Senha</mat-label>
        <input
          matInput
          [type]="hidePassword() ? 'password' : 'text'"
          formControlName="password"
          autocomplete="current-password"
        />
        <button
          mat-icon-button
          matSuffix
          type="button"
          (click)="hidePassword.set(!hidePassword())"
          aria-label="Mostrar ou ocultar senha"
        >
          <mat-icon>
            {{ hidePassword() ? 'visibility' : 'visibility_off' }}
          </mat-icon>
        </button>
      </mat-form-field>

      <mat-checkbox formControlName="remember">
        Lembrar de mim
      </mat-checkbox>

      @if (errorMessage()) {
        <p class="error-message">{{ errorMessage() }}</p>
      }

      <button
        mat-flat-button
        type="submit"
        [disabled]="loading()"
      >
        {{ loading() ? 'Entrando...' : 'Entrar' }}
      </button>
    </form>
  </section>
</main>
```

- [ ] **Step 6: Implement responsive SCSS**

`login.component.scss`:

```scss
:host {
  display: block;
  min-height: 100dvh;
}

.login-page {
  display: grid;
  grid-template-columns: minmax(320px, 1.1fr) minmax(360px, 0.9fr);
  min-height: 100dvh;
  background: #f7f9f7;
}

.brand-panel {
  display: flex;
  align-items: flex-end;
  padding: clamp(2rem, 6vw, 6rem);
  color: #fff;
  background:
    linear-gradient(135deg, rgba(16, 92, 60, 0.96), rgba(28, 122, 78, 0.88)),
    radial-gradient(circle at top right, #ff8a34 0, transparent 34%);
}

.brand-content {
  max-width: 680px;

  h1 {
    margin: 1rem 0;
    font-size: clamp(2.5rem, 5vw, 5.6rem);
    line-height: 0.98;
  }

  p {
    max-width: 560px;
    font-size: 1.1rem;
    line-height: 1.7;
    opacity: 0.88;
  }
}

.brand-mark,
.eyebrow {
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.form-panel {
  display: grid;
  place-items: center;
  padding: 2rem;

  form {
    display: grid;
    width: min(100%, 440px);
    gap: 1rem;
  }

  header {
    margin-bottom: 1rem;
  }

  h2 {
    margin: 0.5rem 0;
    font-size: 2rem;
  }

  p {
    color: #647067;
  }

  button[type='submit'] {
    min-height: 48px;
    margin-top: 0.5rem;
  }
}

.error-message {
  margin: 0;
  color: #b3261e;
}

@media (max-width: 820px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .brand-panel {
    min-height: 240px;
    align-items: center;
  }

  .brand-content h1 {
    font-size: clamp(2rem, 9vw, 3.2rem);
  }
}
```

- [ ] **Step 7: Verify tests and build**

```powershell
npm test -- --watch=false --include="src/app/features/login/login.component.spec.ts"
npm run build
```

Expected: testes e build passam.

- [ ] **Step 8: Commit**

```powershell
git add frontend/src/app/features/login
git commit -m "feat: cria tela responsiva de login"
```

---

### Task 7: Define navigation by role

**Files:**
- Create: `frontend/src/app/shared/navigation/navigation-item.ts`
- Create: `frontend/src/app/shared/navigation/navigation.config.ts`
- Create: `frontend/src/app/layout/sidebar/sidebar.component.spec.ts`

**Interfaces:**
- Produces:
  - `NavigationItem`
  - `NAVIGATION_ITEMS`

- [ ] **Step 1: Create navigation files**

```powershell
New-Item -ItemType Directory -Force `
  "C:\Projetos\agrosales\frontend\src\app\shared\navigation"

New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\src\app\shared\navigation\navigation-item.ts", `
  "C:\Projetos\agrosales\frontend\src\app\shared\navigation\navigation.config.ts"
```

- [ ] **Step 2: Implement navigation contract**

`navigation-item.ts`:

```typescript
import { UserRole } from '../../core/models/user-role';

export interface NavigationItem {
  label: string;
  icon: string;
  route: string;
  roles: UserRole[];
}
```

- [ ] **Step 3: Implement navigation configuration**

`navigation.config.ts`:

```typescript
import { UserRole } from '../../core/models/user-role';
import { NavigationItem } from './navigation-item';

const allRoles = [
  UserRole.ADMINISTRADOR,
  UserRole.PRODUTOR,
  UserRole.VENDEDOR,
];

export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    label: 'Dashboard',
    icon: 'dashboard',
    route: '/dashboard',
    roles: allRoles,
  },
  {
    label: 'Produtos',
    icon: 'inventory_2',
    route: '/products',
    roles: allRoles,
  },
  {
    label: 'Variações',
    icon: 'category',
    route: '/product-variations',
    roles: [
      UserRole.ADMINISTRADOR,
      UserRole.PRODUTOR,
    ],
  },
  {
    label: 'Lotes',
    icon: 'warehouse',
    route: '/lots',
    roles: [
      UserRole.ADMINISTRADOR,
      UserRole.PRODUTOR,
    ],
  },
  {
    label: 'Clientes',
    icon: 'groups',
    route: '/customers',
    roles: allRoles,
  },
  {
    label: 'Pedidos',
    icon: 'receipt_long',
    route: '/orders',
    roles: allRoles,
  },
  {
    label: 'Usuários',
    icon: 'manage_accounts',
    route: '/users',
    roles: [UserRole.ADMINISTRADOR],
  },
];
```

- [ ] **Step 4: Commit**

```powershell
git add frontend/src/app/shared/navigation
git commit -m "feat: define navegação por perfil"
```

---

### Task 8: Build responsive app shell, sidebar and topbar

**Files:**
- Create: layout files listed in the File Map.
- Test: `frontend/src/app/layout/sidebar/sidebar.component.spec.ts`

**Interfaces:**
- Consumes: `AuthService.currentUser`, `AuthService.logout`, `NAVIGATION_ITEMS`.
- Produces: `AppShellComponent`, `SidebarComponent`, `TopbarComponent`.

- [ ] **Step 1: Create layout files**

```powershell
cd "C:\Projetos\agrosales\frontend"

New-Item -ItemType Directory -Force `
  "src\app\layout\app-shell", `
  "src\app\layout\sidebar", `
  "src\app\layout\topbar"

New-Item -ItemType File -Force `
  "src\app\layout\app-shell\app-shell.component.ts", `
  "src\app\layout\app-shell\app-shell.component.html", `
  "src\app\layout\app-shell\app-shell.component.scss", `
  "src\app\layout\sidebar\sidebar.component.ts", `
  "src\app\layout\sidebar\sidebar.component.html", `
  "src\app\layout\sidebar\sidebar.component.scss", `
  "src\app\layout\sidebar\sidebar.component.spec.ts", `
  "src\app\layout\topbar\topbar.component.ts", `
  "src\app\layout\topbar\topbar.component.html", `
  "src\app\layout\topbar\topbar.component.scss"
```

- [ ] **Step 2: Write failing sidebar role test**

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { SidebarComponent } from './sidebar.component';

describe('SidebarComponent', () => {
  let fixture: ComponentFixture<SidebarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarComponent],
      providers: [
        {
          provide: AuthService,
          useValue: {
            currentUser: () => ({
              id: '1',
              name: 'Vendedor',
              email: 'vendedor@agrosales.com',
              role: UserRole.VENDEDOR,
            }),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SidebarComponent);
    fixture.detectChanges();
  });

  it('hides admin-only navigation items', () => {
    const labels = fixture.componentInstance.items().map(
      (item) => item.label,
    );

    expect(labels).not.toContain('Usuários');
    expect(labels).not.toContain('Lotes');
    expect(labels).toContain('Pedidos');
  });
});
```

- [ ] **Step 3: Run test and verify failure**

```powershell
npm test -- --watch=false --include="src/app/layout/sidebar/sidebar.component.spec.ts"
```

Expected: FAIL porque sidebar não existe.

- [ ] **Step 4: Implement sidebar**

`sidebar.component.ts`:

```typescript
import { Component, computed } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import {
  RouterLink,
  RouterLinkActive,
} from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';
import { NAVIGATION_ITEMS } from '../../shared/navigation/navigation.config';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    MatIconModule,
    MatListModule,
    RouterLink,
    RouterLinkActive,
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  readonly items = computed(() => {
    const role = this.auth.currentUser()?.role;

    return role
      ? NAVIGATION_ITEMS.filter((item) =>
          item.roles.includes(role),
        )
      : [];
  });

  constructor(readonly auth: AuthService) {}
}
```

`sidebar.component.html`:

```html
<div class="brand">
  <span class="brand-icon">A</span>
  <span>AgroSales</span>
</div>

<nav aria-label="Navegação principal">
  @for (item of items(); track item.route) {
    <a
      mat-list-item
      [routerLink]="item.route"
      routerLinkActive="active"
    >
      <mat-icon matListItemIcon>{{ item.icon }}</mat-icon>
      <span matListItemTitle>{{ item.label }}</span>
    </a>
  }
</nav>
```

`sidebar.component.scss`:

```scss
:host {
  display: block;
  height: 100%;
  background: #0f5c3c;
  color: #fff;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 72px;
  padding: 0 1.25rem;
  font-size: 1.1rem;
  font-weight: 700;
}

.brand-icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 10px;
  color: #0f5c3c;
  background: #fff;
}

nav a {
  margin: 0.25rem 0.75rem;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.82);
}

nav a.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.16);
}
```

- [ ] **Step 5: Implement topbar**

`topbar.component.ts`:

```typescript
import {
  Component,
  EventEmitter,
  Output,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss',
})
export class TopbarComponent {
  @Output() readonly menuToggle =
    new EventEmitter<void>();

  constructor(
    readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  logout(): void {
    this.auth.logout();
    void this.router.navigate(['/login']);
  }
}
```

`topbar.component.html`:

```html
<header>
  <button
    mat-icon-button
    type="button"
    (click)="menuToggle.emit()"
    aria-label="Abrir ou recolher menu"
  >
    <mat-icon>menu</mat-icon>
  </button>

  <div class="spacer"></div>

  @if (auth.currentUser(); as user) {
    <div class="user">
      <span>
        <strong>{{ user.name }}</strong>
        <small>{{ user.role }}</small>
      </span>

      <button
        mat-icon-button
        type="button"
        (click)="logout()"
        aria-label="Sair"
      >
        <mat-icon>logout</mat-icon>
      </button>
    </div>
  }
</header>
```

`topbar.component.scss`:

```scss
header {
  display: flex;
  align-items: center;
  min-height: 72px;
  padding: 0 1rem;
  border-bottom: 1px solid #e5e9e6;
  background: #fff;
}

.spacer {
  flex: 1;
}

.user {
  display: flex;
  align-items: center;
  gap: 0.75rem;

  span {
    display: grid;
    text-align: right;
  }

  small {
    color: #6d786f;
  }
}

@media (max-width: 600px) {
  .user span {
    display: none;
  }
}
```

- [ ] **Step 6: Implement app shell**

`app-shell.component.ts`:

```typescript
import { BreakpointObserver } from '@angular/cdk/layout';
import { Component, ViewChild } from '@angular/core';
import { MatSidenav, MatSidenavModule } from '@angular/material/sidenav';
import { RouterOutlet } from '@angular/router';
import { map } from 'rxjs';

import { SidebarComponent } from '../sidebar/sidebar.component';
import { TopbarComponent } from '../topbar/topbar.component';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    MatSidenavModule,
    RouterOutlet,
    SidebarComponent,
    TopbarComponent,
  ],
  templateUrl: './app-shell.component.html',
  styleUrl: './app-shell.component.scss',
})
export class AppShellComponent {
  @ViewChild(MatSidenav) sidenav?: MatSidenav;

  readonly isMobile$ = this.breakpoints
    .observe('(max-width: 900px)')
    .pipe(map((result) => result.matches));

  constructor(
    private readonly breakpoints: BreakpointObserver,
  ) {}

  toggleMenu(): void {
    void this.sidenav?.toggle();
  }
}
```

`app-shell.component.html`:

```html
<mat-sidenav-container>
  <mat-sidenav
    #sidenav
    [mode]="(isMobile$ | async) ? 'over' : 'side'"
    [opened]="(isMobile$ | async) === false"
  >
    <app-sidebar />
  </mat-sidenav>

  <mat-sidenav-content>
    <app-topbar (menuToggle)="toggleMenu()" />

    <main class="content">
      <router-outlet />
    </main>
  </mat-sidenav-content>
</mat-sidenav-container>
```

Adicione `AsyncPipe` aos imports do componente.

`app-shell.component.scss`:

```scss
mat-sidenav-container {
  min-height: 100dvh;
  background: #f4f7f5;
}

mat-sidenav {
  width: 260px;
  border: 0;
}

.content {
  padding: clamp(1rem, 3vw, 2rem);
}
```

- [ ] **Step 7: Verify tests and build**

```powershell
npm test -- --watch=false --include="src/app/layout/sidebar/sidebar.component.spec.ts"
npm run build
```

Expected: testes e build passam.

- [ ] **Step 8: Commit**

```powershell
git add frontend/src/app/layout
git commit -m "feat: cria layout responsivo autenticado"
```

---

### Task 9: Add placeholder, 403 and 404 pages

**Files:**
- Create: files listed under Features in File Map.

**Interfaces:**
- Produces:
  - `FeaturePlaceholderComponent`
  - `AccessDeniedComponent`
  - `NotFoundComponent`

- [ ] **Step 1: Create files**

```powershell
cd "C:\Projetos\agrosales\frontend"

New-Item -ItemType Directory -Force `
  "src\app\features\placeholder", `
  "src\app\features\access-denied", `
  "src\app\features\not-found"

New-Item -ItemType File -Force `
  "src\app\features\placeholder\feature-placeholder.component.ts", `
  "src\app\features\placeholder\feature-placeholder.component.html", `
  "src\app\features\placeholder\feature-placeholder.component.scss", `
  "src\app\features\access-denied\access-denied.component.ts", `
  "src\app\features\not-found\not-found.component.ts"
```

- [ ] **Step 2: Implement reusable placeholder**

`feature-placeholder.component.ts`:

```typescript
import { Component, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-feature-placeholder',
  standalone: true,
  imports: [MatIconModule],
  templateUrl: './feature-placeholder.component.html',
  styleUrl: './feature-placeholder.component.scss',
})
export class FeaturePlaceholderComponent {
  readonly title = input.required<string>();
  readonly description = input.required<string>();
  readonly icon = input.required<string>();
}
```

`feature-placeholder.component.html`:

```html
<section class="page">
  <nav aria-label="Breadcrumb">
    AgroSales / {{ title() }}
  </nav>

  <header>
    <div>
      <span class="eyebrow">Módulo</span>
      <h1>{{ title() }}</h1>
      <p>{{ description() }}</p>
    </div>

    <mat-icon>{{ icon() }}</mat-icon>
  </header>

  <article>
    <h2>Estrutura pronta</h2>
    <p>
      Este módulo será implementado na próxima etapa do
      AgroSales.
    </p>
  </article>
</section>
```

`feature-placeholder.component.scss`:

```scss
.page {
  display: grid;
  gap: 1.5rem;
}

nav,
p {
  color: #66736a;
}

header,
article {
  padding: clamp(1.25rem, 3vw, 2rem);
  border: 1px solid #e0e6e2;
  border-radius: 18px;
  background: #fff;
}

header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;

  mat-icon {
    width: auto;
    height: auto;
    color: #ef7d2d;
    font-size: 3rem;
  }
}

h1 {
  margin: 0.35rem 0;
  font-size: clamp(2rem, 4vw, 3.4rem);
}

.eyebrow {
  color: #0f5c3c;
  font-weight: 700;
  text-transform: uppercase;
}
```

- [ ] **Step 3: Implement 403 page**

`access-denied.component.ts`:

```typescript
import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-access-denied',
  standalone: true,
  imports: [MatButtonModule, RouterLink],
  template: `
    <main class="status-page">
      <span>403</span>
      <h1>Acesso negado</h1>
      <p>Seu perfil não possui permissão para esta página.</p>
      <a mat-flat-button routerLink="/dashboard">
        Voltar ao Dashboard
      </a>
    </main>
  `,
  styles: [`
    .status-page {
      display: grid;
      min-height: 100dvh;
      place-content: center;
      justify-items: center;
      padding: 2rem;
      text-align: center;
      background: #f4f7f5;
    }

    span {
      color: #ef7d2d;
      font-size: 5rem;
      font-weight: 800;
    }
  `],
})
export class AccessDeniedComponent {}
```

- [ ] **Step 4: Implement 404 page**

`not-found.component.ts`:

```typescript
import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [MatButtonModule, RouterLink],
  template: `
    <main class="status-page">
      <span>404</span>
      <h1>Página não encontrada</h1>
      <p>O endereço informado não existe no AgroSales.</p>
      <a mat-flat-button routerLink="/dashboard">
        Voltar ao Dashboard
      </a>
    </main>
  `,
  styles: [`
    .status-page {
      display: grid;
      min-height: 100dvh;
      place-content: center;
      justify-items: center;
      padding: 2rem;
      text-align: center;
      background: #f4f7f5;
    }

    span {
      color: #0f5c3c;
      font-size: 5rem;
      font-weight: 800;
    }
  `],
})
export class NotFoundComponent {}
```

- [ ] **Step 5: Verify build**

```powershell
npm run build
```

Expected: build passa.

- [ ] **Step 6: Commit**

```powershell
git add frontend/src/app/features
git commit -m "feat: adiciona páginas base 403 e 404"
```

---

### Task 10: Configure complete route tree

**Files:**
- Modify: `frontend/src/app/app.routes.ts`
- Modify: `frontend/src/app/app.component.html`

**Interfaces:**
- Consumes: `authGuard`, `roleGuard`, feature components and `UserRole`.
- Produces: todas as rotas definidas na especificação.

- [ ] **Step 1: Replace root template**

`app.component.html`:

```html
<router-outlet />
```

Confirme que `RouterOutlet` está importado em `app.component.ts`.

- [ ] **Step 2: Implement routes**

`app.routes.ts`:

```typescript
import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { UserRole } from './core/models/user-role';

const allRoles = [
  UserRole.ADMINISTRADOR,
  UserRole.PRODUTOR,
  UserRole.VENDEDOR,
];

const producerRoles = [
  UserRole.ADMINISTRADOR,
  UserRole.PRODUTOR,
];

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./features/login/login.component').then(
        (module) => module.LoginComponent,
      ),
  },
  {
    path: 'access-denied',
    loadComponent: () =>
      import(
        './features/access-denied/access-denied.component'
      ).then((module) => module.AccessDeniedComponent),
  },
  {
    path: '',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./layout/app-shell/app-shell.component').then(
        (module) => module.AppShellComponent,
      ),
    children: [
      {
        path: 'dashboard',
        canActivate: [roleGuard],
        data: { roles: allRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Dashboard',
      },
      {
        path: 'products',
        canActivate: [roleGuard],
        data: { roles: allRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Produtos',
      },
      {
        path: 'product-variations',
        canActivate: [roleGuard],
        data: { roles: producerRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Variações',
      },
      {
        path: 'lots',
        canActivate: [roleGuard],
        data: { roles: producerRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Lotes',
      },
      {
        path: 'customers',
        canActivate: [roleGuard],
        data: { roles: allRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Clientes',
      },
      {
        path: 'orders',
        canActivate: [roleGuard],
        data: { roles: allRoles },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Pedidos',
      },
      {
        path: 'users',
        canActivate: [roleGuard],
        data: { roles: [UserRole.ADMINISTRADOR] },
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then((module) => module.FeaturePlaceholderComponent),
        title: 'Usuários',
      },
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dashboard',
      },
    ],
  },
  {
    path: '**',
    loadComponent: () =>
      import('./features/not-found/not-found.component').then(
        (module) => module.NotFoundComponent,
      ),
  },
];
```

- [ ] **Step 3: Supply route data to placeholder**

Como o mesmo componente será reutilizado, altere `FeaturePlaceholderComponent` para ler `ActivatedRoute.snapshot.title` e uma tabela por rota:

```typescript
private readonly content: Record<
  string,
  { description: string; icon: string }
> = {
  Dashboard: {
    description: 'Visão geral do AgroSales.',
    icon: 'dashboard',
  },
  Produtos: {
    description: 'Cadastro e consulta de produtos.',
    icon: 'inventory_2',
  },
  Variações: {
    description: 'Variações comerciais dos produtos.',
    icon: 'category',
  },
  Lotes: {
    description: 'Controle de lotes e validade.',
    icon: 'warehouse',
  },
  Clientes: {
    description: 'Cadastro e consulta de clientes.',
    icon: 'groups',
  },
  Pedidos: {
    description: 'Fluxo comercial de pedidos.',
    icon: 'receipt_long',
  },
  Usuários: {
    description: 'Gestão de usuários e perfis.',
    icon: 'manage_accounts',
  },
};
```

Exponha `title`, `description` e `icon` como propriedades derivadas da rota e atualize o template para usar propriedades, não inputs.

- [ ] **Step 4: Verify all routes manually**

```powershell
npm start
```

Verifique no navegador:

```text
http://localhost:4200/login
http://localhost:4200/dashboard
http://localhost:4200/products
http://localhost:4200/access-denied
http://localhost:4200/rota-inexistente
```

Expected:
- usuário anônimo é enviado ao login;
- rota inexistente mostra 404;
- layout aparece após sessão válida.

- [ ] **Step 5: Run tests and build**

```powershell
npm test -- --watch=false
npm run build
```

Expected: zero falhas e build com exit code `0`.

- [ ] **Step 6: Commit**

```powershell
git add frontend/src/app
git commit -m "feat: configura rotas e páginas base"
```

---

### Task 11: Apply global theme and final responsive polish

**Files:**
- Modify: `frontend/src/styles.scss`

**Interfaces:**
- Produces: tema global AgroSales e estilos básicos acessíveis.

- [ ] **Step 1: Add global Material theme**

Em `styles.scss`:

```scss
@use '@angular/material' as mat;

html {
  @include mat.theme((
    color: (
      primary: mat.$green-palette,
      tertiary: mat.$orange-palette,
    ),
    typography: Roboto,
    density: 0,
  ));
}

:root {
  color-scheme: light;
  font-family: Roboto, Arial, sans-serif;
  color: #1d2921;
  background: #f4f7f5;
}

* {
  box-sizing: border-box;
}

html,
body {
  min-height: 100%;
  margin: 0;
}

body {
  min-width: 320px;
}

button,
a,
input {
  font: inherit;
}
```

- [ ] **Step 2: Verify desktop and mobile sizes**

Com `npm start`, teste no DevTools:

```text
1440 × 900
1024 × 768
768 × 1024
390 × 844
```

Expected:
- sem overflow horizontal;
- menu sobreposto abaixo de 900 px;
- login empilhado abaixo de 820 px;
- controles utilizáveis por toque.

- [ ] **Step 3: Run complete verification**

```powershell
npm test -- --watch=false
npm run build
```

Expected: zero falhas e build com exit code `0`.

- [ ] **Step 4: Commit**

```powershell
git add frontend/src/styles.scss
git commit -m "style: aplica identidade visual responsiva"
```

---

### Task 12: End-to-end manual acceptance and documentation

**Files:**
- Modify: `README.md`
- Create: `frontend/README.md`

**Interfaces:**
- Produces: instruções de execução e checklist de aceite.

- [ ] **Step 1: Create frontend README**

```powershell
New-Item -ItemType File -Force `
  "C:\Projetos\agrosales\frontend\README.md"
```

Conteúdo mínimo:

```markdown
# AgroSales Frontend

## Requisitos

- Node.js
- npm
- API AgroSales disponível em `http://192.168.100.30:8000`

## Instalação

```powershell
npm install
```

## Desenvolvimento

```powershell
npm start
```

Acesse `http://localhost:4200`.

## Testes

```powershell
npm test -- --watch=false
```

## Build

```powershell
npm run build
```
```

- [ ] **Step 2: Validate real login**

Com backend ativo:

1. Acesse `/orders` sem sessão.
2. Confirme redirecionamento para `/login?returnUrl=%2Forders`.
3. Faça login com usuário válido.
4. Confirme retorno para `/orders`.
5. Marque e desmarque “Lembrar de mim” em logins separados.
6. Reabra a aba e confirme persistência correta.
7. Faça logout e confirme limpeza da sessão.

- [ ] **Step 3: Validate roles**

Teste com cada perfil:

```text
ADMINISTRADOR
PRODUTOR
VENDEDOR
```

Expected:
- itens do menu conforme a matriz;
- acesso direto proibido vai para `/access-denied`.

- [ ] **Step 4: Run final verification**

```powershell
cd "C:\Projetos\agrosales\frontend"

npm test -- --watch=false
npm run build
```

Expected:
- todos os testes passam;
- build termina com exit code `0`.

- [ ] **Step 5: Commit documentation**

```powershell
cd "C:\Projetos\agrosales"

git add frontend/README.md README.md
git commit -m "docs: documenta execução do frontend"
```

- [ ] **Step 6: Inspect final history**

```powershell
git status
git log --oneline -12
```

Expected:
- working tree clean;
- commits incrementais desta implementação presentes.
