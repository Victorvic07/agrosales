import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import {
  ProductVariation,
  ProductVariationCreate,
  ProductVariationUpdate,
} from './product-variation.models';
import { ProductVariationService } from './product-variation.service';

describe('ProductVariationService', () => {
  let service: ProductVariationService;
  let httpMock: HttpTestingController;

  const variationId =
    '2bbce322-d1c8-4ef7-b86b-c9ee59615e7f';

  const variation: ProductVariation = {
    id: variationId,
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
  };

  const createPayload: ProductVariationCreate = {
    product_id:
      'd20377eb-ecc8-4c28-b96d-cac25ce2b60d',
    internal_code: 'TOM-ITA-20-A',
    classification: 'Categoria A',
    package_type: 'Caixa 20 kg',
    unit_of_measure: 'CAIXA',
    weight_or_volume: 20,
    standard_price: 160,
    minimum_price: 145,
    minimum_stock: 10,
    commission_percentage: 3,
    barcode: null,
    qr_code: null,
  };

  const updatePayload: ProductVariationUpdate = {
    classification: 'Premium',
    package_type: 'Caixa 20 kg',
    unit_of_measure: 'CAIXA',
    weight_or_volume: 20,
    standard_price: 180,
    minimum_price: 165,
    minimum_stock: 12,
    commission_percentage: 4,
    barcode: null,
    qr_code: null,
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ProductVariationService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(
      ProductVariationService,
    );

    httpMock = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('lists product variations', () => {
    service.list().subscribe((response) => {
      expect(response).toEqual([variation]);
    });

    const request = httpMock.expectOne(
      '/api/v1/product-variations',
    );

    expect(request.request.method).toBe('GET');

    request.flush([variation]);
  });

  it('creates a product variation', () => {
    service
      .create(createPayload)
      .subscribe((response) => {
        expect(response).toEqual(variation);
      });

    const request = httpMock.expectOne(
      '/api/v1/product-variations',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(
      createPayload,
    );

    request.flush(variation);
  });

  it('updates a product variation', () => {
    service
      .update(variationId, updatePayload)
      .subscribe((response) => {
        expect(response.classification).toBe(
          'Premium',
        );
      });

    const request = httpMock.expectOne(
      `/api/v1/product-variations/${variationId}`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual(
      updatePayload,
    );

    request.flush({
      ...variation,
      ...updatePayload,
    });
  });

  it('updates product variation status', () => {
    service
      .updateStatus(
        variationId,
        {
          is_active: false,
        },
      )
      .subscribe((response) => {
        expect(response.is_active).toBe(false);
      });

    const request = httpMock.expectOne(
      `/api/v1/product-variations/${variationId}/status`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      is_active: false,
    });

    request.flush({
      ...variation,
      is_active: false,
    });
  });
});