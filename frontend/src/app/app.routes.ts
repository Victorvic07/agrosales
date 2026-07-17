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
      import(
        './features/login/login.component'
      ).then(
        (module) =>
          module.LoginComponent,
      ),
  },
  {
    path: 'access-denied',
    loadComponent: () =>
      import(
        './features/access-denied/access-denied.component'
      ).then(
        (module) =>
          module.AccessDeniedComponent,
      ),
  },
  {
    path: '',
    canActivate: [
      authGuard,
    ],
    loadComponent: () =>
      import(
        './layout/app-shell/app-shell.component'
      ).then(
        (module) =>
          module.AppShellComponent,
      ),
    children: [
      {
        path: 'dashboard',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: allRoles,
        },
        title: 'Dashboard',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
      },
      {
        path: 'products',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: allRoles,
        },
        title: 'Produtos',
        loadComponent: () =>
          import(
            './features/products/products.component'
          ).then(
            (module) =>
              module.ProductsComponent,
          ),
      },
      {
        path: 'product-variations',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: producerRoles,
        },
        title: 'Variações',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
      },
      {
        path: 'lots',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: producerRoles,
        },
        title: 'Lotes',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
      },
      {
        path: 'customers',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: allRoles,
        },
        title: 'Clientes',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
      },
      {
        path: 'orders',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: allRoles,
        },
        title: 'Pedidos',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
      },
      {
        path: 'users',
        canActivate: [
          roleGuard,
        ],
        data: {
          roles: [
            UserRole.ADMINISTRADOR,
          ],
        },
        title: 'Usuários',
        loadComponent: () =>
          import(
            './features/placeholder/feature-placeholder.component'
          ).then(
            (module) =>
              module.FeaturePlaceholderComponent,
          ),
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
      import(
        './features/not-found/not-found.component'
      ).then(
        (module) =>
          module.NotFoundComponent,
      ),
  },
];