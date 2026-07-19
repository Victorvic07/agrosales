import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { signal } from '@angular/core';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { Product } from '../products/product.models';
import { ProductService } from '../products/product.service';
import { ProductVariation } from './product-variation.models';
import { ProductVariationService } from './product-variation.service';
import { ProductVariationsComponent } from './product-variations.component';

describe('ProductVariationsComponent status and permissions', () => {
  let fixture: ComponentFixture<ProductVariationsComponent>;
  let component: ProductVariationsComponent;

  const product: Product = {
    id: 'product-1',
    code: 'PROD-001',
    name: 'Tomate Italiano',
    unit: 'QUILOGRAMA',
    custom_unit: null,
    cost_price: '120',
    standard_price: '160',
    minimum_price: '145',
    short_description: null,
    detailed_description: null,
    internal_notes: null,
    image_path: null,
    category_id: null,
    status: 'ATIVO',
  };

  const variation: ProductVariation = {
    id: 'variation-1',
    product_id: 'product-1',
    internal_code: 'TOM-ITA-20-A',
    classification: 'Premium',
    package_type: 'Caixa 20 kg',
    unit_of_measure: 'CAIXA',
    weight_or_volume: '20',
    standard_price: '180',
    minimum_price: '165',
    minimum_stock: '10',
    commission_percentage: '3',
    barcode: null,
    qr_code: null,
    is_active: true,
  };

  const variationServiceMock = {
    list: vi.fn(() => of([variation])),
    create: vi.fn(),
    update: vi.fn(),
    updateStatus: vi.fn(
      (
        variationId: string,
        data: { is_active: boolean },
      ) =>
        of({
          ...variation,
          id: variationId,
          is_active: data.is_active,
        }),
    ),
  };

  const productServiceMock = {
    list: vi.fn(() => of([product])),
  };

  const currentUser = signal<{
    id: string;
    name: string;
    email: string;
    role: UserRole;
  }>({
    id: 'admin-id',
    name: 'Administrador',
    email: 'admin@agrosales.com',
    role: UserRole.ADMINISTRADOR,
  });

  const authServiceMock = {
    currentUser,
  };

  beforeEach(async () => {
    currentUser.set({
      id: 'admin-id',
      name: 'Administrador',
      email: 'admin@agrosales.com',
      role: UserRole.ADMINISTRADOR,
    });

    await TestBed.configureTestingModule({
      imports: [ProductVariationsComponent],
      providers: [
        {
          provide: ProductVariationService,
          useValue: variationServiceMock,
        },
        {
          provide: ProductService,
          useValue: productServiceMock,
        },
        {
          provide: AuthService,
          useValue: authServiceMock,
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      ProductVariationsComponent,
    );
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('allows an administrator to manage variations', () => {
    expect(component.canManage()).toBe(true);

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Nova variação');
    expect(text).toContain('Editar');
    expect(text).toContain('Inativar');
  });

  it('allows a producer to manage variations', () => {
    currentUser.set({
      id: 'producer-id',
      name: 'Produtor',
      email: 'produtor@agrosales.com',
      role: UserRole.PRODUTOR,
    });

    fixture.detectChanges();

    expect(component.canManage()).toBe(true);

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Nova variação');
    expect(text).toContain('Editar');
    expect(text).toContain('Inativar');
  });

  it('keeps the vendor in read-only mode', () => {
    currentUser.set({
      id: 'vendor-id',
      name: 'Vendedor',
      email: 'vendedor@agrosales.com',
      role: UserRole.VENDEDOR,
    });

    fixture.detectChanges();

    expect(component.canManage()).toBe(false);

    const text = fixture.nativeElement.textContent;

    expect(text).not.toContain('Nova variação');
    expect(text).not.toContain('Editar');
    expect(text).not.toContain('Inativar');
    expect(text).not.toContain('Ativar');
    expect(text).toContain('Tomate Italiano');
  });

  it('inactivates a variation and updates the table', () => {
    component.changeStatus(variation);

    expect(
      variationServiceMock.updateStatus,
    ).toHaveBeenCalledWith(
      variation.id,
      {
        is_active: false,
      },
    );

    expect(
      component.variations()[0].is_active,
    ).toBe(false);
  });

  it('activates an inactive variation', () => {
    const inactiveVariation = {
      ...variation,
      is_active: false,
    };

    component.variations.set([
      inactiveVariation,
    ]);

    component.changeStatus(
      inactiveVariation,
    );

    expect(
      variationServiceMock.updateStatus,
    ).toHaveBeenCalledWith(
      inactiveVariation.id,
      {
        is_active: true,
      },
    );

    expect(
      component.variations()[0].is_active,
    ).toBe(true);
  });

  it('shows an error when status update fails', () => {
    variationServiceMock.updateStatus.mockReturnValueOnce(
      throwError(
        () => new Error('failure'),
      ),
    );

    component.changeStatus(variation);

    expect(component.statusError()).toBe(
      'Não foi possível alterar o status da variação.',
    );
  });
});