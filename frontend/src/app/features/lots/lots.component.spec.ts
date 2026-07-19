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
  InventoryMovement,
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
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    updateStatus: vi.fn(),
    listMovements: vi.fn(),
    createMovement: vi.fn(),
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

  it('changes the lot status and updates the list', () => {
    const updatedLot: Lot = {
      ...lots[0],
      status: 'INACTIVE',
    };

    lotServiceMock.updateStatus.mockReturnValue(
      of(updatedLot),
    );

    fixture.detectChanges();

    component.changeStatus(lots[0]);

    expect(
      lotServiceMock.updateStatus,
    ).toHaveBeenCalledWith(
      lots[0].id,
      {
        status: 'INACTIVE',
      },
    );

    expect(
      component.lots().find(
        (lot) => lot.id === lots[0].id,
      ),
    ).toEqual(updatedLot);

    expect(component.statusError()).toBe('');
  });

  it('shows the backend message when status change fails', () => {
    lotServiceMock.updateStatus.mockReturnValue(
      throwError(() => ({
        error: {
          detail:
            'O lote possui quantidade reservada.',
        },
      })),
    );

    fixture.detectChanges();

    component.changeStatus(lots[0]);

    expect(
      component.statusError(),
    ).toBe(
      'O lote possui quantidade reservada.',
    );

    expect(component.lots()[0]).toEqual(
      lots[0],
    );
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

  it('filters active variations by selected product and creates a lot', () => {
    const inactiveVariation: ProductVariation = {
      ...variations[0],
      id: 'variation-inactive',
      internal_code: 'TOM-INATIVA',
      is_active: false,
    };

    variationServiceMock.list.mockReturnValue(
      of([
        ...variations,
        inactiveVariation,
      ]),
    );

    const createdLot: Lot = {
      id: 'lot-created',
      product_variation_id: 'variation-1',
      code: 'LOTE-NOVO-001',
      production_date: '2026-07-19',
      expiration_date: '2026-08-19',
      physical_quantity: '30',
      reserved_quantity: '0',
      available_quantity: '30',
      status: 'ACTIVE',
      expiration_state: 'REGULAR',
      created_at: '2026-07-19T12:00:00Z',
      updated_at: '2026-07-19T12:00:00Z',
    };

    lotServiceMock.create.mockReturnValue(
      of(createdLot),
    );

    fixture.detectChanges();

    component.openCreateForm();

    component.lotForm.controls.product_id.setValue(
      'product-1',
    );

    expect(
      component
        .availableVariations()
        .map((variation) => variation.id),
    ).toEqual([
      'variation-1',
    ]);

    component.lotForm.setValue({
      product_id: 'product-1',
      product_variation_id: 'variation-1',
      code: 'LOTE-NOVO-001',
      production_date: '2026-07-19',
      expiration_date: '2026-08-19',
      initial_quantity: 30,
      initial_entry_reason: 'Entrada inicial',
      notes: 'Primeira entrada',
    });

    component.submitLotForm();

    expect(
      lotServiceMock.create,
    ).toHaveBeenCalledWith({
      product_variation_id: 'variation-1',
      code: 'LOTE-NOVO-001',
      production_date: '2026-07-19',
      expiration_date: '2026-08-19',
      initial_quantity: 30,
      initial_entry_reason: 'Entrada inicial',
      notes: 'Primeira entrada',
    });

    expect(
      component.lots().some(
        (lot) => lot.id === createdLot.id,
      ),
    ).toBe(true);

    expect(component.formOpen()).toBe(false);
  });

  it('requires an entry reason when initial quantity is positive', () => {
    fixture.detectChanges();

    component.openCreateForm();

    component.lotForm.setValue({
      product_id: 'product-1',
      product_variation_id: 'variation-1',
      code: 'LOTE-SEM-MOTIVO',
      production_date: '2026-07-19',
      expiration_date: '2026-08-19',
      initial_quantity: 30,
      initial_entry_reason: '',
      notes: '',
    });

    component.submitLotForm();

    expect(
      lotServiceMock.create,
    ).not.toHaveBeenCalled();

    expect(component.formError()).toContain(
      'motivo',
    );
  });

  it('rejects expiration before production date', () => {
    fixture.detectChanges();

    component.openCreateForm();

    component.lotForm.setValue({
      product_id: 'product-1',
      product_variation_id: 'variation-1',
      code: 'LOTE-DATA-INVALIDA',
      production_date: '2026-07-20',
      expiration_date: '2026-07-19',
      initial_quantity: 0,
      initial_entry_reason: '',
      notes: '',
    });

    component.submitLotForm();

    expect(
      lotServiceMock.create,
    ).not.toHaveBeenCalled();

    expect(component.formError()).toContain(
      'validade',
    );
  });

  it('edits a lot without changing product, variation or balances', () => {
    const updatedLot: Lot = {
      ...lots[0],
      code: 'LOTE-TOMATE-ATUALIZADO',
      production_date: '2026-07-02',
      expiration_date: '2026-08-25',
    };

    lotServiceMock.update.mockReturnValue(
      of(updatedLot),
    );

    fixture.detectChanges();

    component.openEditForm(lots[0]);

    expect(component.editingLot()).toEqual(
      lots[0],
    );

    expect(
      component.lotForm.controls.product_id
        .value,
    ).toBe('product-1');

    expect(
      component.lotForm.controls
        .product_variation_id.value,
    ).toBe('variation-1');

    expect(
      component.lotForm.controls.product_id
        .disabled,
    ).toBe(true);

    expect(
      component.lotForm.controls
        .product_variation_id.disabled,
    ).toBe(true);

    component.lotForm.controls.code.setValue(
      'LOTE-TOMATE-ATUALIZADO',
    );

    component.lotForm.controls
      .production_date
      .setValue('2026-07-02');

    component.lotForm.controls
      .expiration_date
      .setValue('2026-08-25');

    component.submitLotForm();

    expect(
      lotServiceMock.update,
    ).toHaveBeenCalledWith(
      lots[0].id,
      {
        code: 'LOTE-TOMATE-ATUALIZADO',
        production_date: '2026-07-02',
        expiration_date: '2026-08-25',
      },
    );

    expect(
      component.lots().find(
        (lot) => lot.id === lots[0].id,
      ),
    ).toEqual(updatedLot);

    expect(component.formOpen()).toBe(false);
    expect(component.editingLot()).toBeNull();
  });

  it('opens lot details and loads movements in chronological order', () => {
    const detailedLot: Lot = {
      ...lots[0],
      reserved_quantity: '2.000',
      available_quantity: '8.000',
    };

    const olderMovement: InventoryMovement = {
      id: 'movement-1',
      lot_id: lots[0].id,
      user_id: 'user-1',
      user_name: 'Maria',
      movement_type: 'ENTRY',
      quantity: '10.000',
      previous_balance: '0.000',
      new_balance: '10.000',
      reason: 'Entrada inicial',
      notes: null,
      created_at: '2026-07-01T10:00:00Z',
    };

    const newerMovement: InventoryMovement = {
      id: 'movement-2',
      lot_id: lots[0].id,
      user_id: 'user-2',
      user_name: 'João',
      movement_type: 'LOSS',
      quantity: '2.000',
      previous_balance: '10.000',
      new_balance: '8.000',
      reason: 'Produto avariado',
      notes: 'Danos durante o transporte',
      created_at: '2026-07-02T10:00:00Z',
    };

    lotServiceMock.get.mockReturnValue(
      of(detailedLot),
    );

    lotServiceMock.listMovements.mockReturnValue(
      of([
        olderMovement,
        newerMovement,
      ]),
    );

    fixture.detectChanges();

    component.openDetails(lots[0]);

    expect(
      lotServiceMock.get,
    ).toHaveBeenCalledWith(
      lots[0].id,
    );

    expect(
      lotServiceMock.listMovements,
    ).toHaveBeenCalledWith(
      lots[0].id,
    );

    expect(component.detailsOpen()).toBe(true);

    expect(component.selectedLot()).toEqual(
      detailedLot,
    );

    expect(component.movements()).toEqual([
      newerMovement,
      olderMovement,
    ]);

    expect(
      component.detailsLoading(),
    ).toBe(false);

    expect(component.detailsError()).toBe('');
  });

  it('shows an error when lot details cannot be loaded', () => {
    lotServiceMock.get.mockReturnValue(
      throwError(
        () => new Error('Falha na API'),
      ),
    );

    lotServiceMock.listMovements.mockReturnValue(
      of([]),
    );

    fixture.detectChanges();

    component.openDetails(lots[0]);

    expect(component.detailsOpen()).toBe(true);

    expect(
      component.detailsLoading(),
    ).toBe(false);

    expect(
      component.detailsError(),
    ).toBe(
      'Não foi possível carregar os detalhes do lote.',
    );

    expect(component.movements()).toEqual([]);
  });

  it('creates a manual movement and reloads the lot and movement history', () => {
    const updatedLot: Lot = {
      ...lots[0],
      physical_quantity: '15.000',
      available_quantity: '15.000',
    };

    const createdMovement: InventoryMovement = {
      id: 'movement-entry',
      lot_id: lots[0].id,
      user_id: 'user-1',
      user_name: 'Maria',
      movement_type: 'ENTRY',
      quantity: '5.000',
      previous_balance: '10.000',
      new_balance: '15.000',
      reason: 'Compra do fornecedor',
      notes: 'Nota fiscal 123',
      created_at: '2026-07-19T13:00:00Z',
    };

    lotServiceMock.createMovement.mockReturnValue(
      of(createdMovement),
    );

    lotServiceMock.get.mockReturnValue(
      of(updatedLot),
    );

    lotServiceMock.listMovements.mockReturnValue(
      of([
        createdMovement,
      ]),
    );

    fixture.detectChanges();

    component.openMovementForm(lots[0]);

    component.movementForm.setValue({
      movement_type: 'ENTRY',
      quantity: 5,
      reason: 'Compra do fornecedor',
      notes: 'Nota fiscal 123',
    });

    component.submitMovement();

    expect(
      lotServiceMock.createMovement,
    ).toHaveBeenCalledWith({
      lot_id: lots[0].id,
      movement_type: 'ENTRY',
      quantity: 5,
      reason: 'Compra do fornecedor',
      notes: 'Nota fiscal 123',
    });

    expect(
      lotServiceMock.get,
    ).toHaveBeenCalledWith(
      lots[0].id,
    );

    expect(
      lotServiceMock.listMovements,
    ).toHaveBeenCalledWith(
      lots[0].id,
    );

    expect(
      component.lots().find(
        (lot) => lot.id === lots[0].id,
      ),
    ).toEqual(updatedLot);

    expect(component.movements()).toEqual([
      createdMovement,
    ]);

    expect(
      component.movementFormOpen(),
    ).toBe(false);

    expect(component.movementError()).toBe('');
  });

  it('rejects zero quantity for a movement other than adjustment', () => {
    fixture.detectChanges();

    component.openMovementForm(lots[0]);

    component.movementForm.setValue({
      movement_type: 'LOSS',
      quantity: 0,
      reason: 'Produto avariado',
      notes: '',
    });

    component.submitMovement();

    expect(
      lotServiceMock.createMovement,
    ).not.toHaveBeenCalled();

    expect(
      component.movementError(),
    ).toContain(
      'maior que zero',
    );
  });

  it('allows zero quantity for an adjustment movement', () => {
    const adjustedLot: Lot = {
      ...lots[0],
    };

    const adjustmentMovement: InventoryMovement = {
      id: 'movement-adjustment',
      lot_id: lots[0].id,
      user_id: 'user-1',
      user_name: 'Maria',
      movement_type: 'ADJUSTMENT',
      quantity: '0.000',
      previous_balance: '10.000',
      new_balance: '10.000',
      reason: 'Conferência de estoque',
      notes: null,
      created_at: '2026-07-19T14:00:00Z',
    };

    lotServiceMock.createMovement.mockReturnValue(
      of(adjustmentMovement),
    );

    lotServiceMock.get.mockReturnValue(
      of(adjustedLot),
    );

    lotServiceMock.listMovements.mockReturnValue(
      of([
        adjustmentMovement,
      ]),
    );

    fixture.detectChanges();

    component.openMovementForm(lots[0]);

    component.movementForm.setValue({
      movement_type: 'ADJUSTMENT',
      quantity: 0,
      reason: 'Conferência de estoque',
      notes: '',
    });

    component.submitMovement();

    expect(
      lotServiceMock.createMovement,
    ).toHaveBeenCalledWith({
      lot_id: lots[0].id,
      movement_type: 'ADJUSTMENT',
      quantity: 0,
      reason: 'Conferência de estoque',
      notes: null,
    });

    expect(
      component.movementFormOpen(),
    ).toBe(false);
  });

  it('renders the lot management actions and opens the create form', () => {
    fixture.detectChanges();

    const newLotButton =
      fixture.nativeElement.querySelector(
        '[data-testid="new-lot-button"]',
      ) as HTMLButtonElement | null;

    expect(newLotButton).not.toBeNull();

    if (!newLotButton) {
      return;
    }

    newLotButton.click();
    fixture.detectChanges();

    expect(component.formOpen()).toBe(true);

    const formDrawer =
      fixture.nativeElement.querySelector(
        '[data-testid="lot-form-drawer"]',
      ) as HTMLElement | null;

    expect(formDrawer).not.toBeNull();

    expect(
      formDrawer?.textContent,
    ).toContain('Novo lote');

    expect(
      formDrawer?.querySelector(
        '[formControlName="code"]',
      ),
    ).not.toBeNull();

    expect(
      formDrawer?.querySelector(
        '[formControlName="product_variation_id"]',
      ),
    ).not.toBeNull();
  });

  it('renders row actions and opens details and movement panels', () => {
    const movement: InventoryMovement = {
      id: 'movement-ui',
      lot_id: lots[0].id,
      user_id: 'user-1',
      user_name: 'Maria',
      movement_type: 'ENTRY',
      quantity: '10.000',
      previous_balance: '0.000',
      new_balance: '10.000',
      reason: 'Entrada inicial',
      notes: null,
      created_at: '2026-07-19T15:00:00Z',
    };

    lotServiceMock.get.mockReturnValue(
      of(lots[0]),
    );

    lotServiceMock.listMovements.mockReturnValue(
      of([movement]),
    );

    fixture.detectChanges();

    const detailsButton =
      fixture.nativeElement.querySelector(
        `[data-testid="details-${lots[0].id}"]`,
      ) as HTMLButtonElement | null;

    const editButton =
      fixture.nativeElement.querySelector(
        `[data-testid="edit-${lots[0].id}"]`,
      ) as HTMLButtonElement | null;

    const statusButton =
      fixture.nativeElement.querySelector(
        `[data-testid="status-${lots[0].id}"]`,
      ) as HTMLButtonElement | null;

    const movementButton =
      fixture.nativeElement.querySelector(
        `[data-testid="movement-${lots[0].id}"]`,
      ) as HTMLButtonElement | null;

    expect(detailsButton).not.toBeNull();
    expect(editButton).not.toBeNull();
    expect(statusButton).not.toBeNull();
    expect(movementButton).not.toBeNull();

    if (
      !detailsButton ||
      !movementButton
    ) {
      return;
    }

    detailsButton.click();
    fixture.detectChanges();

    expect(component.detailsOpen()).toBe(true);

    const detailsDrawer =
      fixture.nativeElement.querySelector(
        '[data-testid="lot-details-drawer"]',
      ) as HTMLElement | null;

    expect(detailsDrawer).not.toBeNull();

    expect(
      detailsDrawer?.textContent,
    ).toContain(lots[0].code);

    expect(
      detailsDrawer?.textContent,
    ).toContain('Entrada inicial');

    component.closeDetails();
    fixture.detectChanges();

    movementButton.click();
    fixture.detectChanges();

    expect(
      component.movementFormOpen(),
    ).toBe(true);

    const movementDrawer =
      fixture.nativeElement.querySelector(
        '[data-testid="movement-form-drawer"]',
      ) as HTMLElement | null;

    expect(movementDrawer).not.toBeNull();

    expect(
      movementDrawer?.querySelector(
        'option[value="SALE"]',
      ),
    ).toBeNull();

    expect(
      movementDrawer?.querySelector(
        'option[value="ENTRY"]',
      ),
    ).not.toBeNull();

    expect(
      movementDrawer?.querySelector(
        'option[value="LOSS"]',
      ),
    ).not.toBeNull();

    expect(
      movementDrawer?.querySelector(
        'option[value="RETURN"]',
      ),
    ).not.toBeNull();

    expect(
      movementDrawer?.querySelector(
        'option[value="ADJUSTMENT"]',
      ),
    ).not.toBeNull();
  });

});