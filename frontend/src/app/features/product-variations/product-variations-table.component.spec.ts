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
import { ProductVariation } from './product-variation.models';
import { ProductVariationService } from './product-variation.service';
import { ProductVariationsComponent } from './product-variations.component';

describe('ProductVariationsComponent table', () => {
  let fixture: ComponentFixture<ProductVariationsComponent>;
  let component: ProductVariationsComponent;

  const products: Product[] = [
    {
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
    },
    {
      id: 'product-2',
      code: 'PROD-002',
      name: 'Batata Inglesa',
      unit: 'QUILOGRAMA',
      custom_unit: null,
      cost_price: '70',
      standard_price: '100',
      minimum_price: '90',
      short_description: null,
      detailed_description: null,
      internal_notes: null,
      image_path: null,
      category_id: null,
      status: 'ATIVO',
    },
  ];

  const variations: ProductVariation[] = [
    {
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
    },
    {
      id: 'variation-2',
      product_id: 'product-2',
      internal_code: 'BAT-ING-10-B',
      classification: 'Categoria B',
      package_type: 'Saco 10 kg',
      unit_of_measure: 'SACO',
      weight_or_volume: '10',
      standard_price: '100',
      minimum_price: '90',
      minimum_stock: '8',
      commission_percentage: '2',
      barcode: null,
      qr_code: null,
      is_active: false,
    },
  ];

  const variationServiceMock = {
    list: vi.fn(() => of(variations)),
    create: vi.fn(),
    update: vi.fn(),
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
    list: vi.fn(() => of(products)),
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

  it('renders the variation table columns', () => {
    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Produto');
    expect(text).toContain('Código');
    expect(text).toContain('Classificação');
    expect(text).toContain('Embalagem');
    expect(text).toContain('Unidade');
    expect(text).toContain('Preço padrão');
    expect(text).toContain('Preço mínimo');
    expect(text).toContain('Status');
  });

  it('renders the product name and variation code', () => {
    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Tomate Italiano');
    expect(text).toContain('TOM-ITA-20-A');
    expect(text).toContain('Batata Inglesa');
    expect(text).toContain('BAT-ING-10-B');
  });

  it('filters by product name', () => {
    component.searchTerm.set('tomate');
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Tomate Italiano');
    expect(text).not.toContain('Batata Inglesa');
  });

  it('filters by internal code', () => {
    component.searchTerm.set('BAT-ING');
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;

    expect(text).not.toContain('Tomate Italiano');
    expect(text).toContain('Batata Inglesa');
  });

  it('filters by classification', () => {
    component.searchTerm.set('premium');
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Tomate Italiano');
    expect(text).not.toContain('Batata Inglesa');
  });

  it('filters active variations', () => {
    component.statusFilter.set('active');
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;

    expect(text).toContain('Tomate Italiano');
    expect(text).not.toContain('Batata Inglesa');
  });

  it('filters inactive variations', () => {
    component.statusFilter.set('inactive');
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;

    expect(text).not.toContain('Tomate Italiano');
    expect(text).toContain('Batata Inglesa');
  });
});