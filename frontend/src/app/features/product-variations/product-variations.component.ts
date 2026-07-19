import {
  CommonModule,
  registerLocaleData,
} from '@angular/common';
import localePt from '@angular/common/locales/pt';
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
import { forkJoin } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';
import { UserRole } from '../../core/models/user-role';
import { Product } from '../products/product.models';
import { ProductService } from '../products/product.service';
import {
  ProductVariation,
  ProductVariationCreate,
  ProductVariationUpdate,
} from './product-variation.models';
import { ProductVariationService } from './product-variation.service';

registerLocaleData(localePt);

type StatusFilter = 'all' | 'active' | 'inactive';

@Component({
  selector: 'app-product-variations',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
  ],
  templateUrl:
    './product-variations.component.html',
  styleUrl:
    './product-variations.component.scss',
})
export class ProductVariationsComponent
  implements OnInit
{
  private readonly variationService =
    inject(ProductVariationService);

  private readonly productService =
    inject(ProductService);

  private readonly authService =
    inject(AuthService);

  private readonly formBuilder =
    inject(FormBuilder);

  readonly variations =
    signal<ProductVariation[]>([]);

  readonly products =
    signal<Product[]>([]);

  readonly loading = signal(false);

  readonly errorMessage = signal('');

  readonly searchTerm = signal('');

  readonly statusFilter =
    signal<StatusFilter>('all');

  readonly formOpen = signal(false);

  readonly editingVariation =
    signal<ProductVariation | null>(null);

  readonly formError = signal('');

  readonly statusError = signal('');

  readonly saving = signal(false);

  readonly canManage = computed(() => {
    const role =
      this.authService.currentUser()?.role;

    return (
      role === UserRole.ADMINISTRADOR ||
      role === UserRole.PRODUTOR
    );
  });

  readonly variationForm =
    this.formBuilder.nonNullable.group({
      product_id: [
        '',
        Validators.required,
      ],
      internal_code: [
        '',
        Validators.required,
      ],
      classification: [''],
      package_type: [
        '',
        Validators.required,
      ],
      unit_of_measure: [
        '',
        Validators.required,
      ],
      weight_or_volume: [0],
      standard_price: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      minimum_price: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      minimum_stock: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      commission_percentage: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
      barcode: [''],
      qr_code: [''],
    });

  readonly filteredVariations = computed(() => {
    const search = this.searchTerm()
      .trim()
      .toLowerCase();

    const status = this.statusFilter();

    return this.variations().filter(
      (variation) => {
        const matchesStatus =
          status === 'all' ||
          (status === 'active' &&
            variation.is_active) ||
          (status === 'inactive' &&
            !variation.is_active);

        if (!matchesStatus) {
          return false;
        }

        if (!search) {
          return true;
        }

        const productName =
          this.getProductName(
            variation.product_id,
          ).toLowerCase();

        const classification =
          variation.classification
            ?.toLowerCase() ?? '';

        return (
          productName.includes(search) ||
          variation.internal_code
            .toLowerCase()
            .includes(search) ||
          classification.includes(search)
        );
      },
    );
  });

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    this.statusError.set('');

    forkJoin({
      variations:
        this.variationService.list(),
      products:
        this.productService.list(),
    }).subscribe({
      next: ({
        variations,
        products,
      }) => {
        this.variations.set(
          variations,
        );
        this.products.set(products);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'Não foi possível carregar as variações de produtos.',
        );
        this.loading.set(false);
      },
    });
  }

  getProductName(productId: string): string {
    return (
      this.products().find(
        (product) =>
          product.id === productId,
      )?.name ?? 'Produto não encontrado'
    );
  }

  updateSearchTerm(event: Event): void {
    const input =
      event.target as HTMLInputElement;

    this.searchTerm.set(input.value);
  }

  updateStatusFilter(event: Event): void {
    const select =
      event.target as HTMLSelectElement;

    this.statusFilter.set(
      select.value as StatusFilter,
    );
  }

  openCreateForm(): void {
    if (!this.canManage()) {
      return;
    }

    this.editingVariation.set(null);
    this.formError.set('');

    this.variationForm.reset({
      product_id: '',
      internal_code: '',
      classification: '',
      package_type: '',
      unit_of_measure: '',
      weight_or_volume: 0,
      standard_price: 0,
      minimum_price: 0,
      minimum_stock: 0,
      commission_percentage: 0,
      barcode: '',
      qr_code: '',
    });

    this.variationForm.controls.product_id.enable();
    this.variationForm.controls.internal_code.enable();

    this.formOpen.set(true);
  }

  openEditForm(
    variation: ProductVariation,
  ): void {
    if (!this.canManage()) {
      return;
    }

    this.editingVariation.set(variation);
    this.formError.set('');

    this.variationForm.reset({
      product_id: variation.product_id,
      internal_code: variation.internal_code,
      classification:
        variation.classification ?? '',
      package_type: variation.package_type,
      unit_of_measure:
        variation.unit_of_measure,
      weight_or_volume:
        Number(
          variation.weight_or_volume ?? 0,
        ),
      standard_price:
        Number(variation.standard_price),
      minimum_price:
        Number(variation.minimum_price),
      minimum_stock:
        Number(variation.minimum_stock),
      commission_percentage:
        Number(
          variation.commission_percentage,
        ),
      barcode: variation.barcode ?? '',
      qr_code: variation.qr_code ?? '',
    });

    this.variationForm.controls.product_id.disable();
    this.variationForm.controls.internal_code.disable();

    this.formOpen.set(true);
  }

  closeForm(): void {
    this.formOpen.set(false);
    this.formError.set('');
    this.editingVariation.set(null);
  }

  submitForm(): void {
    if (!this.canManage()) {
      return;
    }

    this.formError.set('');

    if (this.variationForm.invalid) {
      this.variationForm.markAllAsTouched();
      this.formError.set(
        'Preencha os campos obrigatórios.',
      );
      return;
    }

    const values =
      this.variationForm.getRawValue();

    if (
      values.minimum_price >
      values.standard_price
    ) {
      this.formError.set(
        'O preço mínimo não pode ser maior que o preço padrão.',
      );
      return;
    }

    const commonData: ProductVariationUpdate = {
      classification:
        values.classification.trim() || null,
      package_type:
        values.package_type.trim(),
      unit_of_measure:
        values.unit_of_measure.trim(),
      weight_or_volume:
        values.weight_or_volume,
      standard_price:
        values.standard_price,
      minimum_price:
        values.minimum_price,
      minimum_stock:
        values.minimum_stock,
      commission_percentage:
        values.commission_percentage,
      barcode:
        values.barcode.trim() || null,
      qr_code:
        values.qr_code.trim() || null,
    };

    this.saving.set(true);

    const editing =
      this.editingVariation();

    const request$ = editing
      ? this.variationService.update(
          editing.id,
          commonData,
        )
      : this.variationService.create({
          ...commonData,
          product_id:
            values.product_id,
          internal_code:
            values.internal_code.trim(),
        } satisfies ProductVariationCreate);

    request$.subscribe({
      next: (savedVariation) => {
        this.variations.update(
          (currentVariations) => {
            const exists =
              currentVariations.some(
                (variation) =>
                  variation.id ===
                  savedVariation.id,
              );

            if (exists) {
              return currentVariations.map(
                (variation) =>
                  variation.id ===
                  savedVariation.id
                    ? savedVariation
                    : variation,
              );
            }

            return [
              ...currentVariations,
              savedVariation,
            ];
          },
        );

        this.saving.set(false);
        this.closeForm();
      },
      error: () => {
        this.saving.set(false);
        this.formError.set(
          'Não foi possível salvar a variação.',
        );
      },
    });
  }

  changeStatus(
    variation: ProductVariation,
  ): void {
    if (!this.canManage()) {
      return;
    }

    this.statusError.set('');

    const nextStatus =
      !variation.is_active;

    this.variationService
      .updateStatus(
        variation.id,
        {
          is_active: nextStatus,
        },
      )
      .subscribe({
        next: (updatedVariation) => {
          this.variations.update(
            (currentVariations) =>
              currentVariations.map(
                (currentVariation) =>
                  currentVariation.id ===
                  updatedVariation.id
                    ? updatedVariation
                    : currentVariation,
              ),
          );
        },
        error: () => {
          this.statusError.set(
            'Não foi possível alterar o status da variação.',
          );
        },
      });
  }
}
