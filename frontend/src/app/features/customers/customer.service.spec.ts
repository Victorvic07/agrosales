import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import {
  Customer,
  CustomerCreate,
  CustomerUpdate,
} from './customer.models';
import { CustomerService } from './customer.service';

describe('CustomerService', () => {
  let service: CustomerService;
  let httpMock: HttpTestingController;

  const customerId =
    '1f67c3d2-4c76-49f4-8455-f5e6038851e4';

  const customer: Customer = {
    id: customerId,
    customer_type: 'INDIVIDUAL',
    document_type: 'CPF',
    document: '12345678909',
    name: 'Maria da Silva',
    phone: '67999999999',
    email: 'maria@example.com',
    street: 'Rua das Flores',
    number: '100',
    complement: null,
    neighborhood: 'Centro',
    city: 'Campo Grande',
    state: 'MS',
    zip_code: '79000000',
    is_active: true,
    created_at: '2026-07-17T12:00:00Z',
    updated_at: '2026-07-17T12:00:00Z',
  };

  const createPayload: CustomerCreate = {
    customer_type: 'INDIVIDUAL',
    document_type: 'CPF',
    document: '12345678909',
    name: 'Maria da Silva',
    phone: '67999999999',
    email: 'maria@example.com',
    street: 'Rua das Flores',
    number: '100',
    complement: null,
    neighborhood: 'Centro',
    city: 'Campo Grande',
    state: 'MS',
    zip_code: '79000000',
  };

  const updatePayload: CustomerUpdate = {
    name: 'Maria Souza',
    phone: '67988888888',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        CustomerService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(CustomerService);
    httpMock = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('lists customers including inactive records', () => {
    service.list().subscribe((response) => {
      expect(response).toEqual([customer]);
    });

    const request = httpMock.expectOne(
      '/api/v1/customers?include_inactive=true',
    );

    expect(request.request.method).toBe('GET');

    request.flush([customer]);
  });

  it('creates a customer', () => {
    service
      .create(createPayload)
      .subscribe((response) => {
        expect(response).toEqual(customer);
      });

    const request = httpMock.expectOne(
      '/api/v1/customers',
    );

    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(
      createPayload,
    );

    request.flush(customer);
  });

  it('updates a customer', () => {
    service
      .update(customerId, updatePayload)
      .subscribe((response) => {
        expect(response).toEqual({
          ...customer,
          ...updatePayload,
        });
      });

    const request = httpMock.expectOne(
      `/api/v1/customers/${customerId}`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual(
      updatePayload,
    );

    request.flush({
      ...customer,
      ...updatePayload,
    });
  });

  it('updates customer status', () => {
    service
      .updateStatus(
        customerId,
        {
          is_active: false,
        },
      )
      .subscribe((response) => {
        expect(response.is_active).toBe(false);
      });

    const request = httpMock.expectOne(
      `/api/v1/customers/${customerId}/status`,
    );

    expect(request.request.method).toBe('PATCH');
    expect(request.request.body).toEqual({
      is_active: false,
    });

    request.flush({
      ...customer,
      is_active: false,
    });
  });
});