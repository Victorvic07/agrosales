import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { signal } from '@angular/core';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { Product } from '../products/product.models';
import { ProductService } from '../products/product.service';
import {
  ProductVariation,
  ProductVariationCreate,
  ProductVariationUpdate,
} from './product-variation.models';
import { ProductVariationService } from './product-variation.service';
import { ProductVariationsComponent } from './product-variations.component';

describe('ProductVariationsComponent form', () => {
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
    create: vi.fn(() => of(variation)),
    update: vi.fn(() => of(variation)),
    updateStatus: vi.fn(),
  };

  const authServiceMock = {
    currentUser: signal({
      id: 'admin-id',
      name: 'Administrador',
      email: 'admin@agrosales.com',
      role: UserRole.ADMINISTRADOR,
    }),
  };

  const productServiceMock = {
    list: vi.fn(() => of([product])),
  };

  beforeEach(async () => {
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

  it('opens an empty form for creation', () => {
    component.openCreateForm();

    expect(component.formOpen()).toBe(true);
    expect(component.editingVariation()).toBeNull();

    expect(
      component.variationForm.controls.product_id.enabled,
    ).toBe(true);

    expect(
      component.variationForm.controls.internal_code.enabled,
    ).toBe(true);

    expect(
      component.variationForm.controls.product_id.value,
    ).toBe('');

    expect(
      component.variationForm.controls.internal_code.value,
    ).toBe('');
  });

  it('opens the edit form with product and code disabled', () => {
    component.openEditForm(variation);

    expect(component.formOpen()).toBe(true);
    expect(component.editingVariation()).toEqual(
      variation,
    );

    expect(
      component.variationForm.controls.product_id.disabled,
    ).toBe(true);

    expect(
      component.variationForm.controls.internal_code.disabled,
    ).toBe(true);

    expect(
      component.variationForm.controls.classification.value,
    ).toBe('Premium');

    expect(
      component.variationForm.controls.standard_price.value,
    ).toBe(180);
  });

  it('creates a product variation', () => {
    component.openCreateForm();

    component.variationForm.setValue({
      product_id: 'product-1',
      internal_code: 'TOM-ITA-20-A',
      classification: 'Premium',
      package_type: 'Caixa 20 kg',
      unit_of_measure: 'CAIXA',
      weight_or_volume: 20,
      standard_price: 180,
      minimum_price: 165,
      minimum_stock: 10,
      commission_percentage: 3,
      barcode: '',
      qr_code: '',
    });

    component.submitForm();

    const expected: ProductVariationCreate = {
      product_id: 'product-1',
      internal_code: 'TOM-ITA-20-A',
      classification: 'Premium',
      package_type: 'Caixa 20 kg',
      unit_of_measure: 'CAIXA',
      weight_or_volume: 20,
      standard_price: 180,
      minimum_price: 165,
      minimum_stock: 10,
      commission_percentage: 3,
      barcode: null,
      qr_code: null,
    };

    expect(
      variationServiceMock.create,
    ).toHaveBeenCalledWith(expected);

    expect(component.formOpen()).toBe(false);
  });

  it('updates a product variation without product and code', () => {
    component.openEditForm(variation);

    component.variationForm.patchValue({
      classification: 'Categoria A',
      standard_price: 190,
      minimum_price: 170,
    });

    component.submitForm();

    const expected: ProductVariationUpdate = {
      classification: 'Categoria A',
      package_type: 'Caixa 20 kg',
      unit_of_measure: 'CAIXA',
      weight_or_volume: 20,
      standard_price: 190,
      minimum_price: 170,
      minimum_stock: 10,
      commission_percentage: 3,
      barcode: null,
      qr_code: null,
    };

    expect(
      variationServiceMock.update,
    ).toHaveBeenCalledWith(
      variation.id,
      expected,
    );

    expect(component.formOpen()).toBe(false);
  });

  it('rejects a minimum price above the standard price', () => {
    component.openCreateForm();

    component.variationForm.patchValue({
      product_id: 'product-1',
      internal_code: 'TOM-ITA-20-A',
      package_type: 'Caixa 20 kg',
      unit_of_measure: 'CAIXA',
      standard_price: 100,
      minimum_price: 120,
      minimum_stock: 10,
      commission_percentage: 3,
    });

    component.submitForm();

    expect(
      variationServiceMock.create,
    ).not.toHaveBeenCalled();

    expect(component.formError()).toBe(
      'O preço mínimo não pode ser maior que o preço padrão.',
    );
  });
});