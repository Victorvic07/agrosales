import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { signal } from '@angular/core';
import {
  Subject,
  of,
  throwError,
} from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { Customer } from './customer.models';
import { CustomerService } from './customer.service';
import { CustomersComponent } from './customers.component';

describe('CustomersComponent', () => {
  let component: CustomersComponent;
  let fixture: ComponentFixture<CustomersComponent>;

  const customers: Customer[] = [
    {
      id: '1f67c3d2-4c76-49f4-8455-f5e6038851e4',
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
    },
    {
      id: 'ad605729-c52e-46f3-89a0-a96213ae10f1',
      customer_type: 'COMPANY',
      document_type: 'CNPJ',
      document: '12345678000195',
      name: 'Agro Campo Ltda.',
      phone: null,
      email: null,
      street: null,
      number: null,
      complement: null,
      neighborhood: null,
      city: 'Dourados',
      state: 'MS',
      zip_code: null,
      is_active: false,
      created_at: '2026-07-17T13:00:00Z',
      updated_at: '2026-07-17T13:00:00Z',
    },
  ];

  const customerServiceMock = {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    updateStatus: vi.fn(),
  };

  const currentUser = signal({
    id: 'user-1',
    name: 'Administrador',
    email: 'admin@agrosales.com',
    role: UserRole.ADMINISTRADOR,
  });

  const authServiceMock = {
    currentUser,
  };

  beforeEach(async () => {
    currentUser.set({
      id: 'user-1',
      name: 'Administrador',
      email: 'admin@agrosales.com',
      role: UserRole.ADMINISTRADOR,
    });

    customerServiceMock.list.mockReturnValue(
      of(customers),
    );

    customerServiceMock.create.mockReturnValue(
      of(customers[0]),
    );

    customerServiceMock.update.mockReturnValue(
      of(customers[0]),
    );

    customerServiceMock.updateStatus.mockReturnValue(
      of(customers[0]),
    );

    await TestBed.configureTestingModule({
      imports: [CustomersComponent],
      providers: [
        {
          provide: CustomerService,
          useValue: customerServiceMock,
        },
        {
          provide: AuthService,
          useValue: authServiceMock,
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(
      CustomersComponent,
    );
    component = fixture.componentInstance;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('loads customers on initialization', () => {
    fixture.detectChanges();

    expect(
      customerServiceMock.list,
    ).toHaveBeenCalledTimes(1);

    expect(component.customers()).toEqual(
      customers,
    );

    expect(component.loading()).toBe(false);
  });

  it('shows a loading state while requesting customers', () => {
    const pendingRequest =
      new Subject<Customer[]>();

    customerServiceMock.list.mockReturnValue(
      pendingRequest,
    );

    fixture = TestBed.createComponent(
      CustomersComponent,
    );
    component = fixture.componentInstance;

    fixture.detectChanges();

    expect(component.loading()).toBe(true);
    expect(component.customers()).toEqual([]);

    pendingRequest.complete();
  });

  it('shows an error when loading fails', () => {
    customerServiceMock.list.mockReturnValue(
      throwError(
        () => new Error('failure'),
      ),
    );

    fixture = TestBed.createComponent(
      CustomersComponent,
    );
    component = fixture.componentInstance;

    fixture.detectChanges();

    expect(component.errorMessage()).toBe(
      'Não foi possível carregar os clientes.',
    );

    expect(component.loading()).toBe(false);
  });

  it('reloads customers when loadCustomers is called', () => {
    fixture.detectChanges();

    customerServiceMock.list.mockClear();

    component.loadCustomers();

    expect(
      customerServiceMock.list,
    ).toHaveBeenCalledTimes(1);

    expect(component.customers()).toEqual(
      customers,
    );
  });

  it('filters customers by name', () => {
    component.customers.set(customers);

    component.updateSearchTerm('maria');

    expect(
      component.filteredCustomers(),
    ).toEqual([customers[0]]);
  });

  it('filters customers by document using digits', () => {
    component.customers.set(customers);

    component.updateSearchTerm(
      '123.456.789-09',
    );

    expect(
      component.filteredCustomers(),
    ).toEqual([customers[0]]);
  });

  it('filters active customers', () => {
    component.customers.set(customers);

    component.updateStatusFilter('ATIVO');

    expect(
      component.filteredCustomers(),
    ).toEqual([customers[0]]);
  });

  it('filters inactive customers', () => {
    component.customers.set(customers);

    component.updateStatusFilter('INATIVO');

    expect(
      component.filteredCustomers(),
    ).toEqual([customers[1]]);
  });

  it('allows status management for administrator', () => {
    currentUser.update((user) => ({
      ...user,
      role: UserRole.ADMINISTRADOR,
    }));

    expect(
      component.canManageStatus(),
    ).toBe(true);
  });

  it('allows status management for producer', () => {
    currentUser.update((user) => ({
      ...user,
      role: UserRole.PRODUTOR,
    }));

    expect(
      component.canManageStatus(),
    ).toBe(true);
  });

  it('does not allow status management for vendor', () => {
    currentUser.update((user) => ({
      ...user,
      role: UserRole.VENDEDOR,
    }));

    expect(
      component.canManageStatus(),
    ).toBe(false);
  });

  it('formats the customer city and state', () => {
    expect(
      component.displayCityState(
        customers[0],
      ),
    ).toBe('Campo Grande/MS');

    expect(
      component.displayCityState({
        ...customers[0],
        city: null,
        state: null,
      }),
    ).toBe('-');
  });

  it('opens an empty form for a new customer', () => {
    component.openCreatePanel();

    expect(component.panelOpen()).toBe(true);
    expect(
      component.editingCustomer(),
    ).toBeNull();

    expect(
      component.customerForm.getRawValue(),
    ).toEqual({
      customer_type: 'INDIVIDUAL',
      document_type: 'CPF',
      document: '',
      name: '',
      phone: '',
      email: '',
      street: '',
      number: '',
      complement: '',
      neighborhood: '',
      city: '',
      state: '',
      zip_code: '',
    });
  });

  it('fills the form when editing a customer', () => {
    component.openEditPanel(customers[0]);

    expect(component.panelOpen()).toBe(true);
    expect(
      component.editingCustomer(),
    ).toEqual(customers[0]);

    expect(
      component.customerForm.value.name,
    ).toBe('Maria da Silva');

    expect(
      component.customerForm.value.document,
    ).toBe('12345678909');

    expect(
      component.addressExpanded(),
    ).toBe(true);
  });

  it('closes the customer panel', () => {
    component.openCreatePanel();

    component.closePanel();

    expect(component.panelOpen()).toBe(false);
    expect(
      component.editingCustomer(),
    ).toBeNull();
  });

  it('changes document type according to customer type', () => {
    component.openCreatePanel();

    component.customerForm.controls
      .customer_type
      .setValue('COMPANY');

    expect(
      component.customerForm.controls
        .document_type.value,
    ).toBe('CNPJ');

    component.customerForm.controls
      .customer_type
      .setValue('INDIVIDUAL');

    expect(
      component.customerForm.controls
        .document_type.value,
    ).toBe('CPF');
  });

  it('does not save an invalid customer form', () => {
    component.openCreatePanel();

    component.saveCustomer();

    expect(
      customerServiceMock.create,
    ).not.toHaveBeenCalled();

    expect(
      customerServiceMock.update,
    ).not.toHaveBeenCalled();
  });

  it('creates a customer and adds it to the list', () => {
    const createdCustomer: Customer = {
      ...customers[0],
      id: 'new-customer-id',
      name: 'João da Silva',
      document: '98765432100',
      phone: null,
      email: null,
      street: null,
      number: null,
      complement: null,
      neighborhood: null,
      city: null,
      state: null,
      zip_code: null,
    };

    customerServiceMock.create.mockReturnValue(
      of(createdCustomer),
    );

    component.customers.set(customers);
    component.openCreatePanel();

    component.customerForm.patchValue({
      customer_type: 'INDIVIDUAL',
      document_type: 'CPF',
      document: '987.654.321-00',
      name: 'João da Silva',
    });

    component.saveCustomer();

    expect(
      customerServiceMock.create,
    ).toHaveBeenCalledWith({
      customer_type: 'INDIVIDUAL',
      document_type: 'CPF',
      document: '98765432100',
      name: 'João da Silva',
      phone: null,
      email: null,
      street: null,
      number: null,
      complement: null,
      neighborhood: null,
      city: null,
      state: null,
      zip_code: null,
    });

    expect(component.customers()).toEqual([
      ...customers,
      createdCustomer,
    ]);

    expect(component.panelOpen()).toBe(false);
  });

  it('updates a customer and replaces it in the list', () => {
    const updatedCustomer: Customer = {
      ...customers[0],
      name: 'Maria Souza',
    };

    customerServiceMock.update.mockReturnValue(
      of(updatedCustomer),
    );

    component.customers.set(customers);
    component.openEditPanel(customers[0]);

    component.customerForm.patchValue({
      name: 'Maria Souza',
    });

    component.saveCustomer();

    expect(
      customerServiceMock.update,
    ).toHaveBeenCalledWith(
      customers[0].id,
      expect.objectContaining({
        name: 'Maria Souza',
      }),
    );

    expect(component.customers()[0]).toEqual(
      updatedCustomer,
    );

    expect(component.panelOpen()).toBe(false);
  });

  it('shows the backend error when saving fails', () => {
    customerServiceMock.create.mockReturnValue(
      throwError(() => ({
        error: {
          detail:
            'Já existe um cliente com este documento',
        },
      })),
    );

    component.openCreatePanel();

    component.customerForm.patchValue({
      customer_type: 'INDIVIDUAL',
      document_type: 'CPF',
      document: '12345678909',
      name: 'Maria da Silva',
    });

    component.saveCustomer();

    expect(component.errorMessage()).toBe(
      'Já existe um cliente com este documento',
    );

    expect(component.panelOpen()).toBe(true);
  });


  it('formats CPF for display', () => {
    expect(
      component.formatDocument(
        '12345678901',
        'CPF',
      ),
    ).toBe('123.456.789-01');
  });

  it('formats CNPJ for display', () => {
    expect(
      component.formatDocument(
        '12345678000199',
        'CNPJ',
      ),
    ).toBe('12.345.678/0001-99');
  });

  it('formats phone for display', () => {
    expect(
      component.formatPhone(
        '67999999999',
      ),
    ).toBe('(67) 99999-9999');

    expect(
      component.formatPhone(
        '6733334444',
      ),
    ).toBe('(67) 3333-4444');

    expect(
      component.formatPhone(null),
    ).toBe('-');
  });

  it('formats ZIP code for display', () => {
    expect(
      component.formatZipCode(
        '79000000',
      ),
    ).toBe('79000-000');

    expect(
      component.formatZipCode(null),
    ).toBe('-');
  });

  it('shows formatted document and phone in the table', () => {
    component.customers.set(customers);

    fixture.detectChanges();

    const element =
      fixture.nativeElement as HTMLElement;

    expect(element.textContent).toContain(
      '123.456.789-09',
    );

    expect(element.textContent).toContain(
      '(67) 99999-9999',
    );

    expect(element.textContent).toContain(
      '12.345.678/0001-95',
    );
  });


  it('inactivates a customer after confirmation', () => {
    vi.spyOn(window, 'confirm')
      .mockReturnValue(true);

    customerServiceMock.updateStatus.mockReturnValue(
      of({
        ...customers[0],
        is_active: false,
      }),
    );

    component.changeStatus(
      customers[0],
      false,
    );

    expect(
      customerServiceMock.updateStatus,
    ).toHaveBeenCalledWith(
      customers[0].id,
      {
        is_active: false,
      },
    );
  });

  it('does not update status when confirmation is cancelled', () => {
    vi.spyOn(window, 'confirm')
      .mockReturnValue(false);

    component.changeStatus(
      customers[0],
      false,
    );

    expect(
      customerServiceMock.updateStatus,
    ).not.toHaveBeenCalled();
  });

  it('replaces the customer after status update', () => {
    const updatedCustomer: Customer = {
      ...customers[0],
      is_active: false,
    };

    vi.spyOn(window, 'confirm')
      .mockReturnValue(true);

    customerServiceMock.updateStatus.mockReturnValue(
      of(updatedCustomer),
    );

    component.customers.set(customers);

    component.changeStatus(
      customers[0],
      false,
    );

    expect(component.customers()[0]).toEqual(
      updatedCustomer,
    );
  });

  it('prevents vendor from changing customer status', () => {
    currentUser.update((user) => ({
      ...user,
      role: UserRole.VENDEDOR,
    }));

    vi.spyOn(window, 'confirm')
      .mockReturnValue(true);

    component.changeStatus(
      customers[0],
      false,
    );

    expect(
      customerServiceMock.updateStatus,
    ).not.toHaveBeenCalled();
  });

  it('shows backend error when status update fails', () => {
    vi.spyOn(window, 'confirm')
      .mockReturnValue(true);

    customerServiceMock.updateStatus.mockReturnValue(
      throwError(() => ({
        error: {
          detail:
            'Não foi possível inativar este cliente',
        },
      })),
    );

    component.changeStatus(
      customers[0],
      false,
    );

    expect(component.errorMessage()).toBe(
      'Não foi possível inativar este cliente',
    );
  });

});