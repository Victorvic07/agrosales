import {
  HttpErrorResponse,
} from '@angular/common/http';

import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import {
  forkJoin,
} from 'rxjs';

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
  ExpirationState,
  InventoryMovement,
  InventoryMovementCreate,
  Lot,
  LotCreate,
  LotStatus,
  LotUpdate,
  ManualMovementType,
} from './lot.models';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import {
  toSignal,
} from '@angular/core/rxjs-interop';

import {
  LotService,
} from './lot.service';

type StatusFilter =
  | 'all'
  | LotStatus;

type ExpirationFilter =
  | 'all'
  | ExpirationState;

type AvailabilityFilter =
  | 'all'
  | 'AVAILABLE'
  | 'UNAVAILABLE';

@Component({
  selector: 'app-lots',
  standalone: true,
  imports: [
    ReactiveFormsModule,
  ],
  templateUrl: './lots.component.html',
  styleUrl: './lots.component.scss',
})
export class LotsComponent
  implements OnInit
{
  private readonly lotService =
    inject(LotService);

  private readonly productService =
    inject(ProductService);

  private readonly variationService =
    inject(ProductVariationService);

  private readonly formBuilder =
    inject(FormBuilder);

  readonly lots = signal<Lot[]>([]);

  readonly products =
    signal<Product[]>([]);

  readonly variations =
    signal<ProductVariation[]>([]);

  readonly loading = signal(false);

  readonly errorMessage = signal('');

  readonly statusError = signal('');

  readonly detailsOpen = signal(false);

  readonly selectedLot =
    signal<Lot | null>(null);

  readonly movements =
    signal<InventoryMovement[]>([]);

  readonly detailsLoading = signal(false);

  readonly detailsError = signal('');

  readonly movementFormOpen =
    signal(false);

  readonly movementLot =
    signal<Lot | null>(null);

  readonly movementError = signal('');

  readonly movementSaving =
    signal(false);

  readonly movementForm =
    this.formBuilder.nonNullable.group({
      movement_type: [
        'ENTRY' as ManualMovementType,
        Validators.required,
      ],
      quantity: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      reason: [
        '',
        Validators.required,
      ],
      notes: [''],
    });

  readonly formOpen = signal(false);

  readonly editingLot =
    signal<Lot | null>(null);

  readonly formError = signal('');

  readonly saving = signal(false);

  readonly lotForm =
    this.formBuilder.nonNullable.group({
      product_id: [
        '',
        Validators.required,
      ],
      product_variation_id: [
        '',
        Validators.required,
      ],
      code: [
        '',
        Validators.required,
      ],
      production_date: [
        '',
        Validators.required,
      ],
      expiration_date: [
        '',
        Validators.required,
      ],
      initial_quantity: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      initial_entry_reason: [''],
      notes: [''],
    });

  private readonly selectedProductId =
    toSignal(
      this.lotForm.controls.product_id
        .valueChanges,
      {
        initialValue:
          this.lotForm.controls.product_id
            .value,
      },
    );

  readonly availableVariations =
    computed(() => {
      const productId =
        this.selectedProductId();

      return this.variations().filter(
        (variation) =>
          variation.product_id === productId &&
          variation.is_active,
      );
    });

  readonly searchTerm = signal('');

  readonly productFilter =
    signal<string>('all');

  readonly statusFilter =
    signal<StatusFilter>('all');

  readonly expirationFilter =
    signal<ExpirationFilter>('all');

  readonly availabilityFilter =
    signal<AvailabilityFilter>('all');

  readonly filteredLots = computed(() => {
    const search = this.searchTerm()
      .trim()
      .toLowerCase();

    const productId =
      this.productFilter();

    const status =
      this.statusFilter();

    const expiration =
      this.expirationFilter();

    const availability =
      this.availabilityFilter();

    return this.lots().filter((lot) => {
      const variation =
        this.getVariation(lot);

      const product =
        variation
          ? this.getProduct(
              variation.product_id,
            )
          : undefined;

      const matchesSearch =
        !search ||
        lot.code
          .toLowerCase()
          .includes(search) ||
        variation?.internal_code
          .toLowerCase()
          .includes(search) ||
        variation?.classification
          ?.toLowerCase()
          .includes(search) ||
        product?.name
          .toLowerCase()
          .includes(search) ||
        product?.code
          .toLowerCase()
          .includes(search);

      const matchesProduct =
        productId === 'all' ||
        product?.id === productId;

      const matchesStatus =
        status === 'all' ||
        lot.status === status;

      const matchesExpiration =
        expiration === 'all' ||
        lot.expiration_state === expiration;

      const availableQuantity =
        Number(lot.available_quantity);

      const matchesAvailability =
        availability === 'all' ||
        (
          availability === 'AVAILABLE' &&
          availableQuantity > 0
        ) ||
        (
          availability === 'UNAVAILABLE' &&
          availableQuantity <= 0
        );

      return (
        matchesSearch &&
        matchesProduct &&
        matchesStatus &&
        matchesExpiration &&
        matchesAvailability
      );
    });
  });

  readonly activeLotsCount = computed(
    () =>
      this.lots().filter(
        (lot) =>
          lot.status === 'ACTIVE',
      ).length,
  );

  readonly availableTotal = computed(
    () =>
      this.lots().reduce(
        (total, lot) =>
          total +
          Number(
            lot.available_quantity,
          ),
        0,
      ),
  );

  readonly expiringSoonCount = computed(
    () =>
      this.lots().filter(
        (lot) =>
          lot.expiration_state ===
          'EXPIRING_SOON',
      ).length,
  );

  readonly expiredCount = computed(
    () =>
      this.lots().filter(
        (lot) =>
          lot.expiration_state ===
          'EXPIRED',
      ).length,
  );

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    forkJoin({
      lots: this.lotService.list(),
      products:
        this.productService.list(),
      variations:
        this.variationService.list(),
    }).subscribe({
      next: ({
        lots,
        products,
        variations,
      }) => {
        this.lots.set(lots);
        this.products.set(products);
        this.variations.set(
          variations,
        );
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'Não foi possível carregar os lotes.',
        );
        this.loading.set(false);
      },
    });
  }

  getProductName(lot: Lot): string {
    const variation =
      this.getVariation(lot);

    if (!variation) {
      return 'Produto não encontrado';
    }

    return (
      this.getProduct(
        variation.product_id,
      )?.name ??
      'Produto não encontrado'
    );
  }

  getVariationName(lot: Lot): string {
    return (
      this.getVariation(lot)
        ?.internal_code ??
      'Variação não encontrada'
    );
  }

  updateSearchTerm(
    event: Event,
  ): void {
    const input =
      event.target as HTMLInputElement;

    this.searchTerm.set(input.value);
  }

  updateProductFilter(
    event: Event,
  ): void {
    const select =
      event.target as HTMLSelectElement;

    this.productFilter.set(
      select.value,
    );
  }

  updateStatusFilter(
    event: Event,
  ): void {
    const select =
      event.target as HTMLSelectElement;

    this.statusFilter.set(
      select.value as StatusFilter,
    );
  }

  updateExpirationFilter(
    event: Event,
  ): void {
    const select =
      event.target as HTMLSelectElement;

    this.expirationFilter.set(
      select.value as ExpirationFilter,
    );
  }

  updateAvailabilityFilter(
    event: Event,
  ): void {
    const select =
      event.target as HTMLSelectElement;

    this.availabilityFilter.set(
      select.value as AvailabilityFilter,
    );
  }

  openCreateForm(): void {
    this.editingLot.set(null);
    this.formError.set('');

    this.lotForm.controls.product_id.enable();
    this.lotForm.controls
      .product_variation_id
      .enable();
    this.lotForm.controls
      .initial_quantity
      .enable();
    this.lotForm.controls
      .initial_entry_reason
      .enable();
    this.lotForm.controls.notes.enable();

    this.lotForm.reset({
      product_id: '',
      product_variation_id: '',
      code: '',
      production_date: '',
      expiration_date: '',
      initial_quantity: 0,
      initial_entry_reason: '',
      notes: '',
    });

    this.formOpen.set(true);
  }

  openEditForm(
    lot: Lot,
  ): void {
    const variation =
      this.variations().find(
        (currentVariation) =>
          currentVariation.id ===
          lot.product_variation_id,
      );

    this.editingLot.set(lot);
    this.formError.set('');

    this.lotForm.reset({
      product_id:
        variation?.product_id ?? '',
      product_variation_id:
        lot.product_variation_id,
      code: lot.code,
      production_date:
        lot.production_date,
      expiration_date:
        lot.expiration_date,
      initial_quantity: 0,
      initial_entry_reason: '',
      notes: '',
    });

    this.lotForm.controls.product_id.disable();
    this.lotForm.controls
      .product_variation_id
      .disable();
    this.lotForm.controls
      .initial_quantity
      .disable();
    this.lotForm.controls
      .initial_entry_reason
      .disable();
    this.lotForm.controls.notes.disable();

    this.formOpen.set(true);
  }

  closeForm(): void {
    this.formOpen.set(false);
    this.formError.set('');
    this.editingLot.set(null);
  }

  submitLotForm(): void {
    this.formError.set('');

    if (this.lotForm.invalid) {
      this.lotForm.markAllAsTouched();

      this.formError.set(
        'Preencha os campos obrigatórios.',
      );

      return;
    }

    const values =
      this.lotForm.getRawValue();

    if (
      values.expiration_date <
      values.production_date
    ) {
      this.formError.set(
        'A data de validade não pode ser anterior à data de produção.',
      );

      return;
    }

    const editing =
      this.editingLot();

    if (
      !editing &&
      values.initial_quantity > 0 &&
      !values.initial_entry_reason.trim()
    ) {
      this.formError.set(
        'Informe o motivo da entrada inicial.',
      );

      return;
    }

    this.saving.set(true);

    if (editing) {
      const data: LotUpdate = {
        code: values.code.trim(),
        production_date:
          values.production_date,
        expiration_date:
          values.expiration_date,
      };

      this.lotService
        .update(
          editing.id,
          data,
        )
        .subscribe({
          next: (updatedLot) => {
            this.lots.update(
              (currentLots) =>
                currentLots.map(
                  (lot) =>
                    lot.id === updatedLot.id
                      ? updatedLot
                      : lot,
                ),
            );

            this.saving.set(false);
            this.closeForm();
          },
          error: () => {
            this.saving.set(false);

            this.formError.set(
              'Não foi possível atualizar o lote.',
            );
          },
        });

      return;
    }

    const data: LotCreate = {
      product_variation_id:
        values.product_variation_id,
      code: values.code.trim(),
      production_date:
        values.production_date,
      expiration_date:
        values.expiration_date,
      initial_quantity:
        values.initial_quantity,
      initial_entry_reason:
        values.initial_entry_reason
          .trim() || null,
      notes:
        values.notes.trim() || null,
    };

    this.lotService
      .create(data)
      .subscribe({
        next: (createdLot) => {
          this.lots.update(
            (currentLots) => [
              ...currentLots,
              createdLot,
            ],
          );

          this.saving.set(false);
          this.closeForm();
        },
        error: () => {
          this.saving.set(false);

          this.formError.set(
            'Não foi possível cadastrar o lote.',
          );
        },
      });
  }

  changeStatus(
    lot: Lot,
  ): void {
    this.statusError.set('');

    const nextStatus: LotStatus =
      lot.status === 'ACTIVE'
        ? 'INACTIVE'
        : 'ACTIVE';

    this.lotService
      .updateStatus(
        lot.id,
        {
          status: nextStatus,
        },
      )
      .subscribe({
        next: (updatedLot) => {
          this.lots.update(
            (currentLots) =>
              currentLots.map(
                (currentLot) =>
                  currentLot.id ===
                    updatedLot.id
                    ? updatedLot
                    : currentLot,
              ),
          );
        },
        error: (
          error: HttpErrorResponse,
        ) => {
          const detail =
            error.error?.detail;

          this.statusError.set(
            typeof detail === 'string'
              ? detail
              : 'Não foi possível alterar o status do lote.',
          );
        },
      });
  }

  openDetails(
    lot: Lot,
  ): void {
    this.detailsOpen.set(true);
    this.selectedLot.set(lot);
    this.movements.set([]);
    this.detailsLoading.set(true);
    this.detailsError.set('');

    forkJoin({
      lot: this.lotService.get(
        lot.id,
      ),
      movements:
        this.lotService.listMovements(
          lot.id,
        ),
    }).subscribe({
      next: ({
        lot: detailedLot,
        movements,
      }) => {
        const orderedMovements = [
          ...movements,
        ].sort(
          (first, second) =>
            new Date(
              second.created_at,
            ).getTime() -
            new Date(
              first.created_at,
            ).getTime(),
        );

        this.selectedLot.set(
          detailedLot,
        );

        this.movements.set(
          orderedMovements,
        );

        this.detailsLoading.set(false);
      },
      error: () => {
        this.movements.set([]);

        this.detailsError.set(
          'Não foi possível carregar os detalhes do lote.',
        );

        this.detailsLoading.set(false);
      },
    });
  }

  closeDetails(): void {
    this.detailsOpen.set(false);
    this.selectedLot.set(null);
    this.movements.set([]);
    this.detailsLoading.set(false);
    this.detailsError.set('');
  }

  openMovementForm(
    lot: Lot,
  ): void {
    this.movementLot.set(lot);
    this.movementError.set('');

    this.movementForm.reset({
      movement_type: 'ENTRY',
      quantity: 0,
      reason: '',
      notes: '',
    });

    this.movementFormOpen.set(true);
  }

  closeMovementForm(): void {
    this.movementFormOpen.set(false);
    this.movementLot.set(null);
    this.movementError.set('');
    this.movementSaving.set(false);
  }

  submitMovement(): void {
    this.movementError.set('');

    if (this.movementForm.invalid) {
      this.movementForm.markAllAsTouched();

      this.movementError.set(
        'Preencha os campos obrigatórios.',
      );

      return;
    }

    const lot = this.movementLot();

    if (!lot) {
      this.movementError.set(
        'Selecione um lote para registrar a movimentação.',
      );

      return;
    }

    const values =
      this.movementForm.getRawValue();

    if (
      values.movement_type !==
        'ADJUSTMENT' &&
      values.quantity <= 0
    ) {
      this.movementError.set(
        'A quantidade deve ser maior que zero.',
      );

      return;
    }

    const data: InventoryMovementCreate = {
      lot_id: lot.id,
      movement_type:
        values.movement_type,
      quantity: values.quantity,
      reason: values.reason.trim(),
      notes:
        values.notes.trim() || null,
    };

    this.movementSaving.set(true);

    this.lotService
      .createMovement(data)
      .subscribe({
        next: () => {
          this.reloadAfterMovement(
            lot.id,
          );
        },
        error: (
          error: HttpErrorResponse,
        ) => {
          const detail =
            error.error?.detail;

          this.movementSaving.set(
            false,
          );

          this.movementError.set(
            typeof detail === 'string'
              ? detail
              : 'Não foi possível registrar a movimentação.',
          );
        },
      });
  }

  private reloadAfterMovement(
    lotId: string,
  ): void {
    forkJoin({
      lot: this.lotService.get(
        lotId,
      ),
      movements:
        this.lotService.listMovements(
          lotId,
        ),
    }).subscribe({
      next: ({
        lot,
        movements,
      }) => {
        const orderedMovements = [
          ...movements,
        ].sort(
          (first, second) =>
            new Date(
              second.created_at,
            ).getTime() -
            new Date(
              first.created_at,
            ).getTime(),
        );

        this.lots.update(
          (currentLots) =>
            currentLots.map(
              (currentLot) =>
                currentLot.id === lot.id
                  ? lot
                  : currentLot,
            ),
        );

        if (
          this.selectedLot()?.id ===
          lot.id
        ) {
          this.selectedLot.set(lot);
        }

        this.movements.set(
          orderedMovements,
        );

        this.movementSaving.set(false);
        this.closeMovementForm();
      },
      error: () => {
        this.movementSaving.set(false);

        this.movementError.set(
          'A movimentação foi registrada, mas não foi possível atualizar os dados do lote.',
        );
      },
    });
  }

  private getVariation(
    lot: Lot,
  ): ProductVariation | undefined {
    return this.variations().find(
      (variation) =>
        variation.id ===
        lot.product_variation_id,
    );
  }

  private getProduct(
    productId: string,
  ): Product | undefined {
    return this.products().find(
      (product) =>
        product.id === productId,
    );
  }
}