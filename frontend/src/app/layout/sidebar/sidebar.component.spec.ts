import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import {
  beforeEach,
  describe,
  expect,
  it,
} from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { SidebarComponent } from './sidebar.component';

describe('SidebarComponent', () => {
  let fixture:
    ComponentFixture<SidebarComponent>;

  beforeEach(async () => {
    await TestBed
      .configureTestingModule({
        imports: [
          SidebarComponent,
        ],
        providers: [
          provideRouter([]),
          {
            provide: AuthService,
            useValue: {
              currentUser: () => ({
                id: 'user-id',
                name: 'Vendedor',
                email:
                  'vendedor@agrosales.com',
                role:
                  UserRole.VENDEDOR,
              }),
            },
          },
        ],
      })
      .compileComponents();

    fixture =
      TestBed.createComponent(
        SidebarComponent,
      );

    fixture.detectChanges();
  });

  it(
    'shows only the allowed items for the user role',
    () => {
      const labels =
        fixture.componentInstance
          .items()
          .map(
            (item) =>
              item.label,
          );

      expect(labels).toContain(
        'Dashboard',
      );

      expect(labels).toContain(
        'Produtos',
      );

      expect(labels).toContain(
        'Clientes',
      );

      expect(labels).toContain(
        'Pedidos',
      );

      expect(labels).not.toContain(
        'Usuários',
      );

      expect(labels).not.toContain(
        'Lotes',
      );

      expect(labels).not.toContain(
        'Variações',
      );
    },
  );
});