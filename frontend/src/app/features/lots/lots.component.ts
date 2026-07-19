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
  Lot,
  LotStatus,
} from './lot.models';
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

  readonly lots = signal<Lot[]>([]);

  readonly products =
    signal<Product[]>([]);

  readonly variations =
    signal<ProductVariation[]>([]);

  readonly loading = signal(false);

  readonly errorMessage = signal('');

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