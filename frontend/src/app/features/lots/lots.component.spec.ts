import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import {
  of,
  Subject,
  throwError,
} from 'rxjs';
import { vi } from 'vitest';

import {
  ProductVariation,
} from '../product-variations/product-variation.models';
import {
  ProductVariationService,
} from '../product-variations/product-variation.service';
import {
  Product,
} from '../products/product.models';
import {
  ProductService,
} from '../products/product.service';
import {
  Lot,
} from './lot.models';
import {
  LotService,
} from './lot.service';
import {
  LotsComponent,
} from './lots.component';

describe('LotsComponent', () => {
  let fixture: ComponentFixture<LotsComponent>;
  let component: LotsComponent;

  const productServiceMock = {
    list: vi.fn(),
  };

  const variationServiceMock = {
    list: vi.fn(),
  };

  const lotServiceMock = {
    list: vi.fn(),
  };

  const products: Product[] = [
    {
      id: 'product-1',
      category_id: null,
      code: 'PRD-000001',
      name: 'Tomate',
      unit: 'CAIXA',
      custom_unit: null,
      cost_price: '80',
      standard_price: '160',
      minimum_price: '145',
      short_description: null,
      detailed_description: null,
      internal_notes: null,
      image_path: null,
      status: 'ATIVO',
    },
    {
      id: 'product-2',
      category_id: null,
      code: 'PRD-000002',
      name: 'Alface',
      unit: 'CAIXA',
      custom_unit: null,
      cost_price: '30',
      standard_price: '60',
      minimum_price: '50',
      short_description: null,
      detailed_description: null,
      internal_notes: null,
      image_path: null,
      status: 'ATIVO',
    },
  ];

  const variations: ProductVariation[] = [
    {
      id: 'variation-1',
      product_id: 'product-1',
      internal_code: 'TOM-ITA-20-A',
      classification: 'Categoria A',
      package_type: 'Caixa 20 kg',
      unit_of_measure: 'CAIXA',
      weight_or_volume: '20',
      standard_price: '160',
      minimum_price: '145',
      minimum_stock: '10',
      commission_percentage: '3',
      barcode: null,
      qr_code: null,
      is_active: true,
    },
    {
      id: 'variation-2',
      product_id: 'product-2',
      internal_code: 'ALF-CRE-10',
      classification: 'Crespa',
      package_type: 'Caixa 10 unidades',
      unit_of_measure: 'CAIXA',
      weight_or_volume: null,
      standard_price: '60',
      minimum_price: '50',
      minimum_stock: '5',
      commission_percentage: '3',
      barcode: null,
      qr_code: null,
      is_active: true,
    },
  ];

  const lots: Lot[] = [
    {
      id: 'lot-1',
      product_variation_id: 'variation-1',
      code: 'LOTE-TOMATE-001',
      production_date: '2026-07-01',
      expiration_date: '2026-08-20',
      physical_quantity: '100',
      reserved_quantity: '20',
      available_quantity: '80',
      status: 'ACTIVE',
      expiration_state: 'REGULAR',
      created_at: '2026-07-01T10:00:00Z',
      updated_at: '2026-07-01T10:00:00Z',
    },
    {
      id: 'lot-2',
      product_variation_id: 'variation-2',
      code: 'LOTE-ALFACE-001',
      production_date: '2026-07-01',
      expiration_date: '2026-07-18',
      physical_quantity: '10',
      reserved_quantity: '10',
      available_quantity: '0',
      status: 'INACTIVE',
      expiration_state: 'EXPIRED',
      created_at: '2026-07-01T10:00:00Z',
      updated_at: '2026-07-01T10:00:00Z',
    },
    {
      id: 'lot-3',
      product_variation_id: 'variation-1',
      code: 'LOTE-TOMATE-002',
      production_date: '2026-07-10',
      expiration_date: '2026-07-25',
      physical_quantity: '15',
      reserved_quantity: '0',
      available_quantity: '15',
      status: 'ACTIVE',
      expiration_state: 'EXPIRING_SOON',
      created_at: '2026-07-10T10:00:00Z',
      updated_at: '2026-07-10T10:00:00Z',
    },
  ];

  beforeEach(async () => {
    vi.useFakeTimers();

    vi.setSystemTime(
      new Date('2026-07-19T12:00:00Z'),
    );

    lotServiceMock.list.mockReturnValue(
      of(lots),
    );

    productServiceMock.list.mockReturnValue(
      of(products),
    );

    variationServiceMock.list.mockReturnValue(
      of(variations),
    );

    await TestBed.configureTestingModule({
      imports: [
        LotsComponent,
      ],
      providers: [
        {
          provide: LotService,
          useValue: lotServiceMock,
        },
        {
          provide: ProductService,
          useValue: productServiceMock,
        },
        {
          provide: ProductVariationService,
          useValue: variationServiceMock,
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      LotsComponent,
    );

    component = fixture.componentInstance;
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('loads lots, products and variations', () => {
    fixture.detectChanges();

    expect(
      lotServiceMock.list,
    ).toHaveBeenCalledOnce();

    expect(
      productServiceMock.list,
    ).toHaveBeenCalledOnce();

    expect(
      variationServiceMock.list,
    ).toHaveBeenCalledOnce();

    expect(component.lots()).toEqual(
      lots,
    );

    expect(component.products()).toEqual(
      products,
    );

    expect(component.variations()).toEqual(
      variations,
    );

    expect(
      component.getProductName(lots[0]),
    ).toBe('Tomate');

    expect(
      component.getVariationName(lots[0]),
    ).toBe('TOM-ITA-20-A');
  });

  it('keeps loading active until all data is received', () => {
    const lotsSubject =
      new Subject<Lot[]>();

    lotServiceMock.list.mockReturnValue(
      lotsSubject,
    );

    fixture.detectChanges();

    expect(component.loading()).toBe(true);

    lotsSubject.next(lots);
    lotsSubject.complete();

    expect(component.loading()).toBe(false);
  });

  it('shows an error when loading fails', () => {
    lotServiceMock.list.mockReturnValue(
      throwError(
        () => new Error('Falha na API'),
      ),
    );

    fixture.detectChanges();

    expect(component.loading()).toBe(false);

    expect(component.errorMessage()).toBe(
      'Não foi possível carregar os lotes.',
    );
  });

  it('filters by search, product, status, expiration and availability', () => {
    fixture.detectChanges();

    component.searchTerm.set('tomate');
    component.productFilter.set(
      'product-1',
    );
    component.statusFilter.set('ACTIVE');
    component.expirationFilter.set(
      'EXPIRING_SOON',
    );
    component.availabilityFilter.set(
      'AVAILABLE',
    );

    expect(
      component.filteredLots().map(
        (lot) => lot.id,
      ),
    ).toEqual([
      'lot-3',
    ]);
  });

  it('calculates the four summary cards', () => {
    fixture.detectChanges();

    expect(
      component.activeLotsCount(),
    ).toBe(2);

    expect(
      component.availableTotal(),
    ).toBe(95);

    expect(
      component.expiringSoonCount(),
    ).toBe(1);

    expect(
      component.expiredCount(),
    ).toBe(1);
  });

  it('shows the empty state when there are no lots', () => {
    lotServiceMock.list.mockReturnValue(
      of([]),
    );

    fixture.detectChanges();

    const content =
      fixture.nativeElement.textContent;

    expect(content).toContain(
      'Nenhum lote encontrado.',
    );
  });
});