import { CommonModule } from '@angular/common';
import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import {
  Customer,
  CustomerCreate,
  CustomerType,
  DocumentType,
} from './customer.models';
import { CustomerService } from './customer.service';

type CustomerStatusFilter =
  | 'TODOS'
  | 'ATIVO'
  | 'INATIVO';

@Component({
  selector: 'app-customers',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './customers.component.html',
  styleUrl: './customers.component.scss',
})
export class CustomersComponent
  implements OnInit
{
  private readonly customerService =
    inject(CustomerService);

  private readonly authService =
    inject(AuthService);

  private readonly formBuilder =
    inject(FormBuilder);

  readonly customers =
    signal<Customer[]>([]);

  readonly loading = signal(false);

  readonly errorMessage = signal('');

  readonly searchTerm = signal('');

  readonly statusFilter =
    signal<CustomerStatusFilter>('TODOS');


  readonly panelOpen = signal(false);

  readonly editingCustomer =
    signal<Customer | null>(null);

  readonly addressExpanded =
    signal(false);

  readonly saving = signal(false);

  readonly customerForm =
    this.formBuilder.nonNullable.group({
      customer_type:
        this.formBuilder.nonNullable.control<CustomerType>(
          'INDIVIDUAL',
          {
            validators: [
              Validators.required,
            ],
          },
        ),
      document_type:
        this.formBuilder.nonNullable.control<DocumentType>(
          'CPF',
          {
            validators: [
              Validators.required,
            ],
          },
        ),
      document:
        this.formBuilder.nonNullable.control(
          '',
          {
            validators: [
              Validators.required,
            ],
          },
        ),
      name:
        this.formBuilder.nonNullable.control(
          '',
          {
            validators: [
              Validators.required,
            ],
          },
        ),
      phone:
        this.formBuilder.nonNullable.control(''),
      email:
        this.formBuilder.nonNullable.control(
          '',
          {
            validators: [
              Validators.email,
            ],
          },
        ),
      street:
        this.formBuilder.nonNullable.control(''),
      number:
        this.formBuilder.nonNullable.control(''),
      complement:
        this.formBuilder.nonNullable.control(''),
      neighborhood:
        this.formBuilder.nonNullable.control(''),
      city:
        this.formBuilder.nonNullable.control(''),
      state:
        this.formBuilder.nonNullable.control(''),
      zip_code:
        this.formBuilder.nonNullable.control(''),
    });

  readonly filteredCustomers = computed(() => {
    const rawSearch =
      this.searchTerm().trim();

    const textSearch =
      rawSearch.toLowerCase();

    const documentSearch =
      rawSearch.replace(/\D/g, '');

    return this.customers().filter(
      (customer) => {
        const matchesName =
          !textSearch ||
          customer.name
            .toLowerCase()
            .includes(textSearch);

        const matchesDocument =
          documentSearch.length > 0 &&
          customer.document.includes(
            documentSearch,
          );

        const matchesSearch =
          !rawSearch ||
          matchesName ||
          matchesDocument;

        const currentStatus =
          this.statusFilter();

        const matchesStatus =
          currentStatus === 'TODOS' ||
          (
            currentStatus === 'ATIVO'
              ? customer.is_active
              : !customer.is_active
          );

        return (
          matchesSearch &&
          matchesStatus
        );
      },
    );
  });

  readonly canManageStatus =
    computed(() => {
      const role =
        this.authService.currentUser()
          ?.role;

      return (
        role ===
          UserRole.ADMINISTRADOR ||
        role === UserRole.PRODUTOR
      );
    });

  constructor() {
    this.customerForm.controls
      .customer_type
      .valueChanges
      .subscribe((customerType) => {
        this.customerForm.controls
          .document_type
          .setValue(
            customerType === 'COMPANY'
              ? 'CNPJ'
              : 'CPF',
            {
              emitEvent: false,
            },
          );
      });
  }

  ngOnInit(): void {
    this.loadCustomers();
  }

  loadCustomers(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.customerService
      .list()
      .subscribe({
        next: (customers) => {
          this.customers.set(
            customers,
          );
          this.loading.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'Não foi possível carregar os clientes.',
          );
          this.loading.set(false);
        },
      });
  }

  updateSearchTerm(
    value: string,
  ): void {
    this.searchTerm.set(value);
  }

  updateStatusFilter(
    value: CustomerStatusFilter,
  ): void {
    this.statusFilter.set(value);
  }

  displayCityState(
    customer: Customer,
  ): string {
    if (
      customer.city &&
      customer.state
    ) {
      return `${customer.city}/${customer.state}`;
    }

    return (
      customer.city ??
      customer.state ??
      '-'
    );
  }

  displayDocument(
    customer: Customer,
  ): string {
    return this.formatDocument(
      customer.document,
      customer.document_type,
    );
  }

  formatDocument(
    document: string | null,
    documentType: DocumentType,
  ): string {
    if (!document) {
      return '-';
    }

    const digits =
      document.replace(/\D/g, '');

    if (
      documentType === 'CPF' &&
      digits.length === 11
    ) {
      return digits.replace(
        /(\d{3})(\d{3})(\d{3})(\d{2})/,
        '$1.$2.$3-$4',
      );
    }

    if (
      documentType === 'CNPJ' &&
      digits.length === 14
    ) {
      return digits.replace(
        /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
        '$1.$2.$3/$4-$5',
      );
    }

    return document;
  }

  formatPhone(
    phone: string | null,
  ): string {
    if (!phone) {
      return '-';
    }

    const digits =
      phone.replace(/\D/g, '');

    if (digits.length === 11) {
      return digits.replace(
        /(\d{2})(\d{5})(\d{4})/,
        '($1) $2-$3',
      );
    }

    if (digits.length === 10) {
      return digits.replace(
        /(\d{2})(\d{4})(\d{4})/,
        '($1) $2-$3',
      );
    }

    return phone;
  }

  formatZipCode(
    zipCode: string | null,
  ): string {
    if (!zipCode) {
      return '-';
    }

    const digits =
      zipCode.replace(/\D/g, '');

    if (digits.length === 8) {
      return digits.replace(
        /(\d{5})(\d{3})/,
        '$1-$2',
      );
    }

    return zipCode;
  }

  openCreatePanel(): void {
    this.editingCustomer.set(null);
    this.errorMessage.set('');
    this.addressExpanded.set(false);

    this.customerForm.reset({
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

    this.panelOpen.set(true);
  }

  openEditPanel(
    customer: Customer,
  ): void {
    this.editingCustomer.set(customer);
    this.errorMessage.set('');

    this.customerForm.reset({
      customer_type:
        customer.customer_type,
      document_type:
        customer.document_type,
      document: customer.document,
      name: customer.name,
      phone: customer.phone ?? '',
      email: customer.email ?? '',
      street: customer.street ?? '',
      number: customer.number ?? '',
      complement:
        customer.complement ?? '',
      neighborhood:
        customer.neighborhood ?? '',
      city: customer.city ?? '',
      state: customer.state ?? '',
      zip_code:
        customer.zip_code ?? '',
    });

    this.addressExpanded.set(
      [
        customer.street,
        customer.number,
        customer.complement,
        customer.neighborhood,
        customer.city,
        customer.state,
        customer.zip_code,
      ].some(Boolean),
    );

    this.panelOpen.set(true);
  }

  closePanel(): void {
    this.panelOpen.set(false);
    this.editingCustomer.set(null);
    this.saving.set(false);
  }

  toggleAddress(): void {
    this.addressExpanded.update(
      (expanded) => !expanded,
    );
  }

  saveCustomer(): void {
    if (
      this.customerForm.invalid ||
      this.saving()
    ) {
      this.customerForm
        .markAllAsTouched();
      return;
    }

    this.saving.set(true);
    this.errorMessage.set('');

    const payload =
      this.buildCustomerPayload();

    const editingCustomer =
      this.editingCustomer();

    const request = editingCustomer
      ? this.customerService.update(
          editingCustomer.id,
          payload,
        )
      : this.customerService.create(
          payload,
        );

    request.subscribe({
      next: (savedCustomer) => {
        if (editingCustomer) {
          this.replaceCustomerInList(
            savedCustomer,
          );
        } else {
          this.customers.update(
            (customers) => [
              ...customers,
              savedCustomer,
            ],
          );
        }

        this.closePanel();
      },
      error: (error: {
        error?: {
          detail?: string;
        };
      }) => {
        this.errorMessage.set(
          error.error?.detail ??
            'Não foi possível salvar o cliente.',
        );
        this.saving.set(false);
      },
    });
  }

  changeStatus(
    customer: Customer,
    isActive: boolean,
  ): void {
    if (
      !this.canManageStatus() ||
      customer.is_active === isActive
    ) {
      return;
    }

    const action =
      isActive ? 'ativar' : 'inativar';

    const confirmed =
      window.confirm(
        `Deseja ${action} o cliente "${customer.name}"?`,
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage.set('');

    this.customerService
      .updateStatus(
        customer.id,
        {
          is_active: isActive,
        },
      )
      .subscribe({
        next: (updatedCustomer) => {
          this.replaceCustomerInList(
            updatedCustomer,
          );
        },
        error: (error: {
          error?: {
            detail?: string;
          };
        }) => {
          this.errorMessage.set(
            error.error?.detail ??
              'Não foi possível alterar o status do cliente.',
          );
        },
      });
  }

  private buildCustomerPayload():
    CustomerCreate {
    const value =
      this.customerForm.getRawValue();

    return {
      customer_type:
        value.customer_type,
      document_type:
        value.document_type,
      document:
        value.document.replace(
          /\D/g,
          '',
        ),
      name: value.name.trim(),
      phone:
        this.nullableDigits(
          value.phone,
        ),
      email:
        this.nullableText(
          value.email,
        ),
      street:
        this.nullableText(
          value.street,
        ),
      number:
        this.nullableText(
          value.number,
        ),
      complement:
        this.nullableText(
          value.complement,
        ),
      neighborhood:
        this.nullableText(
          value.neighborhood,
        ),
      city:
        this.nullableText(
          value.city,
        ),
      state:
        this.nullableText(
          value.state,
        )?.toUpperCase() ?? null,
      zip_code:
        this.nullableDigits(
          value.zip_code,
        ),
    };
  }

  private nullableText(
    value: string,
  ): string | null {
    const normalized = value.trim();

    return normalized || null;
  }

  private nullableDigits(
    value: string,
  ): string | null {
    const normalized =
      value.replace(/\D/g, '');

    return normalized || null;
  }

  private replaceCustomerInList(
    updatedCustomer: Customer,
  ): void {
    this.customers.update(
      (customers) =>
        customers.map((customer) =>
          customer.id ===
          updatedCustomer.id
            ? updatedCustomer
            : customer,
        ),
    );
  }
}
