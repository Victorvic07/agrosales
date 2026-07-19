import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import {
  Subject,
  of,
  throwError,
} from 'rxjs';
import { vi } from 'vitest';

import { Product } from '../products/product.models';
import { ProductService } from '../products/product.service';
import { ProductVariation } from './product-variation.models';
import { ProductVariationService } from './product-variation.service';
import { ProductVariationsComponent } from './product-variations.component';

describe('ProductVariationsComponent', () => {
  let component: ProductVariationsComponent;
  let fixture: ComponentFixture<ProductVariationsComponent>;

  const variations: ProductVariation[] = [
    {
      id: '2bbce322-d1c8-4ef7-b86b-c9ee59615e7f',
      product_id:
        'd20377eb-ecc8-4c28-b96d-cac25ce2b60d',
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
  ];

  const products: Product[] = [
    {
      id: 'd20377eb-ecc8-4c28-b96d-cac25ce2b60d',
      code: 'PROD-0001',
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
  ];

  const variationServiceMock = {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    updateStatus: vi.fn(),
  };

  const productServiceMock = {
    list: vi.fn(),
  };

  beforeEach(async () => {
    variationServiceMock.list.mockReturnValue(
      of(variations),
    );

    productServiceMock.list.mockReturnValue(
      of(products),
    );

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
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      ProductVariationsComponent,
    );

    component = fixture.componentInstance;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('loads variations and products on initialization', () => {
    fixture.detectChanges();

    expect(
      variationServiceMock.list,
    ).toHaveBeenCalledTimes(1);

    expect(
      productServiceMock.list,
    ).toHaveBeenCalledTimes(1);

    expect(component.variations()).toEqual(
      variations,
    );

    expect(component.products()).toEqual(
      products,
    );

    expect(component.loading()).toBe(false);
  });

  it('shows loading while requests are pending', () => {
    const variationsRequest =
      new Subject<ProductVariation[]>();

    const productsRequest =
      new Subject<Product[]>();

    variationServiceMock.list.mockReturnValue(
      variationsRequest,
    );

    productServiceMock.list.mockReturnValue(
      productsRequest,
    );

    fixture = TestBed.createComponent(
      ProductVariationsComponent,
    );

    component = fixture.componentInstance;

    fixture.detectChanges();

    expect(component.loading()).toBe(true);
    expect(component.variations()).toEqual([]);
    expect(component.products()).toEqual([]);

    variationsRequest.complete();
    productsRequest.complete();
  });

  it('shows an error when variations fail to load', () => {
    variationServiceMock.list.mockReturnValue(
      throwError(
        () => new Error('failure'),
      ),
    );

    fixture = TestBed.createComponent(
      ProductVariationsComponent,
    );

    component = fixture.componentInstance;

    fixture.detectChanges();

    expect(component.errorMessage()).toBe(
      'Não foi possível carregar as variações de produtos.',
    );

    expect(component.loading()).toBe(false);
  });

  it('shows an error when products fail to load', () => {
    productServiceMock.list.mockReturnValue(
      throwError(
        () => new Error('failure'),
      ),
    );

    fixture = TestBed.createComponent(
      ProductVariationsComponent,
    );

    component = fixture.componentInstance;

    fixture.detectChanges();

    expect(component.errorMessage()).toBe(
      'Não foi possível carregar as variações de produtos.',
    );

    expect(component.loading()).toBe(false);
  });

  it('reloads variations and products', () => {
    fixture.detectChanges();

    variationServiceMock.list.mockClear();
    productServiceMock.list.mockClear();

    component.loadData();

    expect(
      variationServiceMock.list,
    ).toHaveBeenCalledTimes(1);

    expect(
      productServiceMock.list,
    ).toHaveBeenCalledTimes(1);
  });
});