import {
  provideHttpClient,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import {
  TestBed,
} from '@angular/core/testing';

import {
  InventoryMovement,
  InventoryMovementCreate,
  Lot,
  LotCreate,
  LotStatusUpdate,
  LotUpdate,
} from './lot.models';
import {
  LotService,
} from './lot.service';

describe('LotService', () => {
  let service: LotService;
  let httpTesting: HttpTestingController;

  const lot: Lot = {
    id: 'lot-1',
    product_variation_id: 'variation-1',
    code: 'LOTE-001',
    production_date: '2026-07-01',
    expiration_date: '2026-07-31',
    physical_quantity: '100',
    reserved_quantity: '20',
    available_quantity: '80',
    status: 'ACTIVE',
    expiration_state: 'REGULAR',
    created_at: '2026-07-01T10:00:00Z',
    updated_at: '2026-07-01T10:00:00Z',
  };

  const movement: InventoryMovement = {
    id: 'movement-1',
    lot_id: lot.id,
    user_id: 'user-1',
    user_name: 'Produtor',
    movement_type: 'ENTRY',
    quantity: '100',
    previous_balance: '0',
    new_balance: '100',
    reason: 'Entrada inicial',
    notes: null,
    created_at: '2026-07-01T10:00:00Z',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(
      LotService,
    );

    httpTesting = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('lists lots', () => {
    service.list().subscribe((lots) => {
      expect(lots).toEqual([lot]);
    });

    const request = httpTesting.expectOne(
      '/api/v1/lots',
    );

    expect(request.request.method).toBe(
      'GET',
    );

    request.flush([lot]);
  });

  it('gets a lot by id', () => {
    service.get(lot.id).subscribe(
      (response) => {
        expect(response).toEqual(lot);
      },
    );

    const request = httpTesting.expectOne(
      `/api/v1/lots/${lot.id}`,
    );

    expect(request.request.method).toBe(
      'GET',
    );

    request.flush(lot);
  });

  it('creates a lot', () => {
    const data: LotCreate = {
      product_variation_id:
        lot.product_variation_id,
      code: 'LOTE-001',
      production_date: '2026-07-01',
      expiration_date: '2026-07-31',
      initial_quantity: 100,
      initial_entry_reason:
        'Entrada inicial',
      notes: null,
    };

    service.create(data).subscribe(
      (response) => {
        expect(response).toEqual(lot);
      },
    );

    const request = httpTesting.expectOne(
      '/api/v1/lots',
    );

    expect(request.request.method).toBe(
      'POST',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(lot);
  });

  it('updates a lot', () => {
    const data: LotUpdate = {
      code: 'LOTE-001-ATUALIZADO',
      production_date: '2026-07-02',
      expiration_date: '2026-08-01',
    };

    service.update(
      lot.id,
      data,
    ).subscribe((response) => {
      expect(response).toEqual(lot);
    });

    const request = httpTesting.expectOne(
      `/api/v1/lots/${lot.id}`,
    );

    expect(request.request.method).toBe(
      'PUT',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(lot);
  });

  it('updates lot status', () => {
    const data: LotStatusUpdate = {
      status: 'INACTIVE',
    };

    service.updateStatus(
      lot.id,
      data,
    ).subscribe((response) => {
      expect(response).toEqual(lot);
    });

    const request = httpTesting.expectOne(
      `/api/v1/lots/${lot.id}/status`,
    );

    expect(request.request.method).toBe(
      'PATCH',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(lot);
  });

  it('lists movements from a lot', () => {
    service.listMovements(
      lot.id,
    ).subscribe((movements) => {
      expect(movements).toEqual([
        movement,
      ]);
    });

    const request = httpTesting.expectOne(
      `/api/v1/inventory-movements?lot_id=${lot.id}`,
    );

    expect(request.request.method).toBe(
      'GET',
    );

    request.flush([movement]);
  });

  it('creates a manual inventory movement', () => {
    const data: InventoryMovementCreate = {
      lot_id: lot.id,
      movement_type: 'LOSS',
      quantity: 5,
      reason: 'Produto avariado',
      notes: null,
    };

    service.createMovement(
      data,
    ).subscribe((response) => {
      expect(response).toEqual(movement);
    });

    const request = httpTesting.expectOne(
      '/api/v1/inventory-movements',
    );

    expect(request.request.method).toBe(
      'POST',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(movement);
  });
});