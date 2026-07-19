import {
  CommonModule,
} from '@angular/common';
import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import {
  FormBuilder,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import {
  MatButtonModule,
} from '@angular/material/button';
import {
  MatFormFieldModule,
} from '@angular/material/form-field';
import {
  MatIconModule,
} from '@angular/material/icon';
import {
  MatInputModule,
} from '@angular/material/input';
import {
  MatProgressSpinnerModule,
} from '@angular/material/progress-spinner';
import {
  MatSelectModule,
} from '@angular/material/select';
import {
  forkJoin,
  of,
  switchMap,
} from 'rxjs';

import {
  AuthService,
} from '../../core/auth/auth.service';
import {
  UserRole,
} from '../../core/models/user-role';
import {
  Category,
  Product,
  ProductCreate,
  ProductStatus,
} from './product.models';
import {
  ProductService,
} from './product.service';

type ProductStatusFilter =
  ProductStatus | 'TODOS';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl:
    './products.component.html',
  styleUrl:
    './products.component.scss',
})
export class ProductsComponent
  implements OnInit {
  private readonly productService =
    inject(ProductService);

  private readonly authService =
    inject(AuthService);

  private readonly formBuilder =
    inject(FormBuilder);

  readonly products =
    signal<Product[]>([]);

  readonly categories =
    signal<Category[]>([]);

  readonly activeCategories =
    computed(() =>
      this.categories().filter(
        (category) => category.is_active,
      ),
    );

  readonly searchTerm =
    signal('');

  readonly statusFilter =
    signal<ProductStatusFilter>(
      'TODOS',
    );

  readonly loading =
    signal(false);

  readonly errorMessage =
    signal('');

  readonly saving =
    signal(false);

  readonly panelOpen =
    signal(false);

  readonly editingProduct =
    signal<Product | null>(null);

  readonly selectedImage =
    signal<File | null>(null);

  readonly imagePreviewUrl =
    signal<string | null>(null);

  readonly productForm =
    this.formBuilder.nonNullable.group({
      code: [''],
      category_id: [
        '',
        Validators.required,
      ],
      name: [
        '',
        Validators.required,
      ],
      unit: [
        'UNIDADE',
        Validators.required,
      ],
      custom_unit: [''],
      cost_price: [
        0,
        [
          Validators.required,
          Validators.min(0),
        ],
      ],
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
      short_description: [''],
      detailed_description: [''],
      internal_notes: [''],
    });

  readonly canManageProducts =
    computed(() => {
      const role =
        this.authService
          .currentUser()
          ?.role;

      return (
        role ===
          UserRole.ADMINISTRADOR ||
        role ===
          UserRole.PRODUTOR
      );
    });

  readonly canDeleteProducts =
    computed(
      () =>
        this.authService
          .currentUser()
          ?.role ===
        UserRole.ADMINISTRADOR,
    );

  readonly filteredProducts =
    computed(() => {
      const search =
        this.searchTerm()
          .trim()
          .toLocaleLowerCase(
            'pt-BR',
          );

      const status =
        this.statusFilter();

      return this.products().filter(
        (product) => {
          const matchesSearch =
            !search ||
            product.name
              .toLocaleLowerCase(
                'pt-BR',
              )
              .includes(search) ||
            product.code
              .toLocaleLowerCase(
                'pt-BR',
              )
              .includes(search);

          const matchesStatus =
            status === 'TODOS' ||
            product.status === status;

          return (
            matchesSearch &&
            matchesStatus
          );
        },
      );
    });

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    forkJoin({
      products: this.productService.list(),
      categories:
        this.productService.listCategories(),
    }).subscribe({
      next: ({
        products,
        categories,
      }) => {
        this.products.set(products);
        this.categories.set(categories);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'Não foi possível carregar os produtos.',
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
    value: ProductStatusFilter,
  ): void {
    this.statusFilter.set(value);
  }

  openCreatePanel(): void {
    this.errorMessage.set('');
    this.clearImageSelection();
    this.editingProduct.set(null);

    this.productForm.reset({
      code: '',
      category_id: '',
      name: '',
      unit: 'UNIDADE',
      custom_unit: '',
      cost_price: 0,
      standard_price: 0,
      minimum_price: 0,
      short_description: '',
      detailed_description: '',
      internal_notes: '',
    });

    this.panelOpen.set(true);
  }

  openEditPanel(
    product: Product,
  ): void {
    this.errorMessage.set('');
    this.clearImageSelection();
    this.editingProduct.set(product);
    this.imagePreviewUrl.set(
      this.productService.imageUrl(product),
    );

    this.productForm.reset({
      code: product.code,
      category_id:
        product.category_id ?? '',
      name: product.name,
      unit: product.unit,
      custom_unit:
        product.custom_unit ?? '',
      cost_price:
        Number(product.cost_price),
      standard_price:
        Number(product.standard_price),
      minimum_price:
        Number(product.minimum_price),
      short_description:
        product.short_description ?? '',
      detailed_description:
        product.detailed_description ?? '',
      internal_notes:
        product.internal_notes ?? '',
    });

    this.panelOpen.set(true);
  }

  closePanel(): void {
    this.panelOpen.set(false);
    this.editingProduct.set(null);
    this.clearImageSelection();
  }

  onImageSelected(
    event: Event,
  ): void {
    const input =
      event.target as HTMLInputElement;

    const file =
      input.files?.[0];

    if (file) {
      this.selectImage(file);
    }
  }

  selectImage(
    file: File,
  ): void {
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/webp',
    ];

    if (
      !allowedTypes.includes(
        file.type,
      )
    ) {
      this.errorMessage.set(
        'Selecione uma imagem JPG, PNG ou WebP.',
      );

      return;
    }

    this.clearPreviewUrl();

    this.selectedImage.set(file);

    const previewUrl =
      typeof URL.createObjectURL ===
      'function'
        ? URL.createObjectURL(file)
        : file.name;

    this.imagePreviewUrl.set(
      previewUrl,
    );

    this.errorMessage.set('');
  }

  removeCurrentImage(): void {
    const product =
      this.editingProduct();

    if (!product) {
      this.clearImageSelection();
      return;
    }

    this.saving.set(true);
    this.errorMessage.set('');

    this.productService
      .removeImage(product.id)
      .subscribe({
        next: (updatedProduct) => {
          this.replaceProductInList(
            updatedProduct,
          );

          this.editingProduct.set(
            updatedProduct,
          );

          this.clearImageSelection();
          this.saving.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'Não foi possível remover a imagem.',
          );

          this.saving.set(false);
        },
      });
  }

  private clearImageSelection(): void {
    this.clearPreviewUrl();
    this.selectedImage.set(null);
    this.imagePreviewUrl.set(null);
  }

  private clearPreviewUrl(): void {
    const previewUrl =
      this.imagePreviewUrl();

    if (
      previewUrl?.startsWith(
        'blob:',
      ) &&
      typeof URL.revokeObjectURL ===
        'function'
    ) {
      URL.revokeObjectURL(
        previewUrl,
      );
    }
  }

  saveProduct(): void {
    if (
      this.productForm.invalid ||
      this.saving()
    ) {
      this.productForm.markAllAsTouched();
      return;
    }

    const data =
      this.buildProductPayload();

    const editingProduct =
      this.editingProduct();

    this.saving.set(true);
    this.errorMessage.set('');

    const request = editingProduct
      ? this.productService.update(
          editingProduct.id,
          data,
        )
      : this.productService.create(
          data,
        );

    request
      .pipe(
        switchMap(
          (savedProduct) => {
            const image =
              this.selectedImage();

            if (!image) {
              return of(savedProduct);
            }

            return this.productService
              .uploadImage(
                savedProduct.id,
                image,
              );
          },
        ),
      )
      .subscribe({
        next: (savedProduct) => {
          this.replaceProductInList(
            savedProduct,
          );

          this.saving.set(false);
          this.closePanel();
        },
        error: () => {
          this.errorMessage.set(
            'Não foi possível salvar o produto.',
          );

          this.saving.set(false);
        },
      });
  }

  private buildProductPayload():
    ProductCreate {
    const value =
      this.productForm.getRawValue();

    return {
      category_id: value.category_id,
      code:
        value.code.trim() || null,
      name: value.name.trim(),
      unit:
        value.unit as ProductCreate['unit'],
      custom_unit:
        value.unit === 'OUTRO'
          ? (
              value.custom_unit.trim() ||
              null
            )
          : null,
      cost_price:
        Number(value.cost_price),
      standard_price:
        Number(value.standard_price),
      minimum_price:
        Number(value.minimum_price),
      short_description:
        value.short_description.trim() ||
        null,
      detailed_description:
        value.detailed_description.trim() ||
        null,
      internal_notes:
        value.internal_notes.trim() ||
        null,
    };
  }

  private replaceProductInList(
    savedProduct: Product,
  ): void {
    const currentProducts =
      this.products();

    const index =
      currentProducts.findIndex(
        (product) =>
          product.id ===
          savedProduct.id,
      );

    if (index === -1) {
      this.products.set([
        savedProduct,
        ...currentProducts,
      ]);

      return;
    }

    this.products.set(
      currentProducts.map(
        (product) =>
          product.id ===
          savedProduct.id
            ? savedProduct
            : product,
      ),
    );
  }

  changeStatus(
    product: Product,
    status: ProductStatus,
  ): void {
    if (product.status === status) {
      return;
    }

    const confirmed =
      window.confirm(
        `Deseja alterar o status de "${product.name}"?`,
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage.set('');

    this.productService
      .updateStatus(
        product.id,
        {
          status,
        },
      )
      .subscribe({
        next: (updatedProduct) => {
          this.replaceProductInList(
            updatedProduct,
          );
        },
        error: () => {
          this.errorMessage.set(
            'Não foi possível alterar o status do produto.',
          );
        },
      });
  }

  deleteProduct(
    product: Product,
  ): void {
    if (!this.canDeleteProducts()) {
      return;
    }

    const confirmed =
      window.confirm(
        `Deseja excluir o produto "${product.name}"?`,
      );

    if (!confirmed) {
      return;
    }

    this.errorMessage.set('');

    this.productService
      .delete(product.id)
      .subscribe({
        next: () => {
          this.products.update(
            (products) =>
              products.filter(
                (currentProduct) =>
                  currentProduct.id !==
                  product.id,
              ),
          );
        },
        error: (error: {
          error?: {
            detail?: string;
          };
        }) => {
          this.errorMessage.set(
            error.error?.detail ??
              'Não foi possível excluir o produto.',
          );
        },
      });
  }

  displayUnit(
    product: Product,
  ): string {
    if (
      product.unit === 'OUTRO' &&
      product.custom_unit
    ) {
      return product.custom_unit;
    }

    const labels:
      Record<string, string> = {
        UNIDADE: 'Unidade',
        QUILOGRAMA: 'Quilograma',
        GRAMA: 'Grama',
        LITRO: 'Litro',
        MILILITRO: 'Mililitro',
        CAIXA: 'Caixa',
        PACOTE: 'Pacote',
        SACO: 'Saco',
        OUTRO: 'Outro',
      };

    return (
      labels[product.unit] ??
      product.unit
    );
  }

  displayStatus(
    status: ProductStatus,
  ): string {
    const labels:
      Record<ProductStatus, string> = {
        ATIVO: 'Ativo',
        INATIVO: 'Inativo',
        DESCONTINUADO:
          'Descontinuado',
      };

    return labels[status];
  }

  imageUrl(
    product: Product,
  ): string | null {
    return this.productService
      .imageUrl(product);
  }
}
