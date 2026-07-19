import {
  registerLocaleData,
} from '@angular/common';
import localePt from '@angular/common/locales/pt';
import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import {
  signal,
} from '@angular/core';
import {
  of,
  throwError,
} from 'rxjs';

import {
  AuthService,
} from '../../core/auth/auth.service';
import {
  UserRole,
} from '../../core/models/user-role';
import {
  Product,
} from './product.models';
import {
  ProductService,
} from './product.service';
import {
  ProductsComponent,
} from './products.component';

registerLocaleData(localePt);

describe('ProductsComponent', () => {
  let fixture:
    ComponentFixture<ProductsComponent>;

  let component:
    ProductsComponent;

  const currentUser = signal({
    id: 'user-1',
    name: 'Administrador',
    email: 'admin@agrosales.com',
    role: UserRole.ADMINISTRADOR,
    is_active: true,
  });

  const products: Product[] = [
    {
      id: '1',
      category_id: 'category-1',
      code: 'PRD-000001',
      name: 'Tomate',
      unit: 'UNIDADE',
      custom_unit: null,
      cost_price: '8.50',
      standard_price: '15.00',
      minimum_price: '12.00',
      short_description: null,
      detailed_description: null,
      internal_notes: null,
      image_path: null,
      status: 'ATIVO',
    },
    {
      id: '2',
      category_id: 'category-1',
      code: 'PRD-000002',
      name: 'Alface',
      unit: 'UNIDADE',
      custom_unit: null,
      cost_price: '3.00',
      standard_price: '6.00',
      minimum_price: '5.00',
      short_description: null,
      detailed_description: null,
      internal_notes: null,
      image_path: null,
      status: 'INATIVO',
    },
  ];

  const productServiceMock = {
    list: vi.fn(),
    listCategories: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    uploadImage: vi.fn(),
    removeImage: vi.fn(),
    updateStatus: vi.fn(),
    delete: vi.fn(),
    imageUrl: vi.fn(
      () => null,
    ),
  };

  const authServiceMock = {
    currentUser,
  };

  beforeEach(async () => {
    currentUser.set({
      id: 'user-1',
      name: 'Administrador',
      email: 'admin@agrosales.com',
      role: UserRole.ADMINISTRADOR,
      is_active: true,
    });

    productServiceMock.list
      .mockReturnValue(
        of(products),
      );

    productServiceMock.listCategories
      .mockReturnValue(
        of([
          {
            id: 'category-1',
            name: 'Hortaliças',
            is_active: true,
          },
        ]),
      );

    productServiceMock.create
      .mockReturnValue(
        of(products[0]),
      );

    productServiceMock.update
      .mockReturnValue(
        of(products[0]),
      );

    productServiceMock.uploadImage
      .mockReturnValue(
        of(products[0]),
      );

    productServiceMock.removeImage
      .mockReturnValue(
        of(products[0]),
      );

    productServiceMock.updateStatus
      .mockReturnValue(
        of(products[0]),
      );

    productServiceMock.delete
      .mockReturnValue(
        of(void 0),
      );

    await TestBed
      .configureTestingModule({
        imports: [
          ProductsComponent,
        ],
        providers: [
          {
            provide:
              ProductService,
            useValue:
              productServiceMock,
          },
          {
            provide:
              AuthService,
            useValue:
              authServiceMock,
          },
        ],
      })
      .compileComponents();

    fixture =
      TestBed.createComponent(
        ProductsComponent,
      );

    component =
      fixture.componentInstance;

    fixture.detectChanges();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('loads products on initialization', () => {
    expect(
      productServiceMock.list,
    ).toHaveBeenCalledOnce();

    expect(
      component.products(),
    ).toEqual(products);
  });

  it('filters products by name', () => {
    component.updateSearchTerm(
      'tomate',
    );

    expect(
      component.filteredProducts(),
    ).toEqual([
      products[0],
    ]);
  });

  it('filters products by code', () => {
    component.updateSearchTerm(
      'PRD-000002',
    );

    expect(
      component.filteredProducts(),
    ).toEqual([
      products[1],
    ]);
  });

  it('filters products by status', () => {
    component.updateStatusFilter(
      'INATIVO',
    );

    expect(
      component.filteredProducts(),
    ).toEqual([
      products[1],
    ]);
  });

  it('combines search and status filters', () => {
    component.updateSearchTerm(
      'alface',
    );

    component.updateStatusFilter(
      'ATIVO',
    );

    expect(
      component.filteredProducts(),
    ).toEqual([]);
  });

  it('shows an error when loading fails', () => {
    productServiceMock.list
      .mockReturnValueOnce(
        throwError(
          () => new Error(
            'Falha',
          ),
        ),
      );

    component.loadProducts();

    expect(
      component.errorMessage(),
    ).toBe(
      'Não foi possível carregar os produtos.',
    );

    expect(
      component.loading(),
    ).toBe(false);
  });

  it('allows administrators to manage and delete products', () => {
    expect(
      component.canManageProducts(),
    ).toBe(true);

    expect(
      component.canDeleteProducts(),
    ).toBe(true);
  });

  it('allows producers to manage but not delete products', () => {
    currentUser.set({
      ...currentUser(),
      role: UserRole.PRODUTOR,
    });

    fixture.detectChanges();

    expect(
      component.canManageProducts(),
    ).toBe(true);

    expect(
      component.canDeleteProducts(),
    ).toBe(false);

    expect(
      fixture.nativeElement.querySelector(
        '[data-testid="delete-product-button"]',
      ),
    ).toBeNull();
  });

  it('keeps vendors in read-only mode', () => {
    currentUser.set({
      ...currentUser(),
      role: UserRole.VENDEDOR,
    });

    fixture.detectChanges();

    expect(
      component.canManageProducts(),
    ).toBe(false);

    expect(
      component.canDeleteProducts(),
    ).toBe(false);

    expect(
      fixture.nativeElement.querySelector(
        '[data-testid="new-product-button"]',
      ),
    ).toBeNull();

    expect(
      fixture.nativeElement.querySelector(
        '[data-testid="edit-product-button"]',
      ),
    ).toBeNull();
  });

  it('opens an empty panel for a new product', () => {
    const button =
      fixture.nativeElement.querySelector(
        '[data-testid="new-product-button"]',
      ) as HTMLButtonElement;

    button.click();
    fixture.detectChanges();

    const panel =
      fixture.nativeElement.querySelector(
        '[data-testid="product-panel"]',
      );

    const nameInput =
      fixture.nativeElement.querySelector(
        '[data-testid="product-name-input"]',
      ) as HTMLInputElement | null;

    expect(panel).not.toBeNull();
    expect(nameInput?.value).toBe('');
  });

  it('opens the panel filled when editing a product', () => {
    const button =
      fixture.nativeElement.querySelector(
        '[data-testid="edit-product-button"]',
      ) as HTMLButtonElement;

    button.click();
    fixture.detectChanges();

    const nameInput =
      fixture.nativeElement.querySelector(
        '[data-testid="product-name-input"]',
      ) as HTMLInputElement | null;

    expect(nameInput?.value).toBe(
      'Tomate',
    );
  });

  it('does not submit an invalid product form', () => {
    const button =
      fixture.nativeElement.querySelector(
        '[data-testid="new-product-button"]',
      ) as HTMLButtonElement;

    button.click();
    fixture.detectChanges();

    const submitButton =
      fixture.nativeElement.querySelector(
        '[data-testid="save-product-button"]',
      ) as HTMLButtonElement | null;

    submitButton?.click();
    fixture.detectChanges();

    expect(
      productServiceMock.create,
    ).not.toHaveBeenCalled();
  });

  it('closes the product panel when canceling', () => {
    const button =
      fixture.nativeElement.querySelector(
        '[data-testid="new-product-button"]',
      ) as HTMLButtonElement;

    button.click();
    fixture.detectChanges();

    const cancelButton =
      fixture.nativeElement.querySelector(
        '[data-testid="cancel-product-button"]',
      ) as HTMLButtonElement | null;

    cancelButton?.click();
    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelector(
        '[data-testid="product-panel"]',
      ),
    ).toBeNull();
  });


  it('creates a product from a valid form', () => {
    component.openCreatePanel();

     component.productForm.setValue({
      category_id: 'category-1',
      code: '',
      name: 'Tomate cereja',
      unit: 'UNIDADE',
      custom_unit: '',
      cost_price: 7,
      standard_price: 14,
      minimum_price: 11,
      short_description: '',
      detailed_description: '',
      internal_notes: '',
    });

    fixture.detectChanges();

    const submitButton =
      fixture.nativeElement.querySelector(
        '[data-testid="save-product-button"]',
      ) as HTMLButtonElement;

    submitButton.click();

    expect(
      productServiceMock.create,
    ).toHaveBeenCalledWith({
      category_id: 'category-1',
      code: null,
      name: 'Tomate cereja',
      unit: 'UNIDADE',
      custom_unit: null,
      cost_price: 7,
      standard_price: 14,
      minimum_price: 11,
      short_description: null,
      detailed_description: null,
      internal_notes: null,
    });
  });

  it('updates an existing product from a valid form', () => {
    component.openEditPanel(
      products[0],
    );

    component.productForm.patchValue({
      name: 'Tomate italiano',
    });

    fixture.detectChanges();

    const submitButton =
      fixture.nativeElement.querySelector(
        '[data-testid="save-product-button"]',
      ) as HTMLButtonElement;

    submitButton.click();

    expect(
      productServiceMock.update,
    ).toHaveBeenCalledWith(
      products[0].id,
      expect.objectContaining({
        name: 'Tomate italiano',
      }),
    );
  });

  it('keeps the panel open when saving fails', () => {
    productServiceMock.create
      .mockReturnValueOnce(
        throwError(
          () => new Error(
            'Falha ao salvar',
          ),
        ),
      );

    component.openCreatePanel();

      component.productForm.setValue({
      category_id: 'category-1',
      code: '',
      name: 'Tomate cereja',
      unit: 'UNIDADE',
      custom_unit: '',
      cost_price: 7,
      standard_price: 14,
      minimum_price: 11,
      short_description: '',
      detailed_description: '',
      internal_notes: '',
    });

    fixture.detectChanges();

    const submitButton =
      fixture.nativeElement.querySelector(
        '[data-testid="save-product-button"]',
      ) as HTMLButtonElement;

    submitButton.click();
    fixture.detectChanges();

    expect(
      component.panelOpen(),
    ).toBe(true);

    expect(
      component.errorMessage(),
    ).toBe(
      'Não foi possível salvar o produto.',
    );
  });


  it('stores the selected image and creates a preview', () => {
    component.openCreatePanel();

    const file = new File(
      ['image-content'],
      'tomate.png',
      {
        type: 'image/png',
      },
    );

    component.selectImage(file);

    expect(
      component.selectedImage(),
    ).toBe(file);

    expect(
      component.imagePreviewUrl(),
    ).not.toBeNull();
  });

  it('uploads the selected image after creating a product', () => {
    component.openCreatePanel();

    component.productForm.setValue({
      category_id: 'category-1',
      code: '',
      name: 'Tomate cereja',
      unit: 'UNIDADE',
      custom_unit: '',
      cost_price: 7,
      standard_price: 14,
      minimum_price: 11,
      short_description: '',
      detailed_description: '',
      internal_notes: '',
    });

    const file = new File(
      ['image-content'],
      'tomate.png',
      {
        type: 'image/png',
      },
    );

    component.selectImage(file);
    component.saveProduct();

    expect(
      productServiceMock.uploadImage,
    ).toHaveBeenCalledWith(
      products[0].id,
      file,
    );
  });

  it('removes the current product image', () => {
    const productWithImage: Product = {
      ...products[0],
      image_path:
        'products/tomate.webp',
    };

    component.openEditPanel(
      productWithImage,
    );

    component.removeCurrentImage();

    expect(
      productServiceMock.removeImage,
    ).toHaveBeenCalledWith(
      productWithImage.id,
    );
  });

  it('uses a placeholder when a product has no image', () => {
    productServiceMock.imageUrl
      .mockReturnValueOnce(null);

    fixture.detectChanges();

    expect(
      fixture.nativeElement.querySelector(
        '.product-image mat-icon',
      ),
    ).not.toBeNull();
  });


  it('updates product status after confirmation', () => {
    vi.spyOn(
      window,
      'confirm',
    ).mockReturnValue(true);

    component.changeStatus(
      products[0],
      'INATIVO',
    );

    expect(
      productServiceMock.updateStatus,
    ).toHaveBeenCalledWith(
      products[0].id,
      {
        status: 'INATIVO',
      },
    );
  });

  it('does not update product status when confirmation is canceled', () => {
    vi.spyOn(
      window,
      'confirm',
    ).mockReturnValue(false);

    component.changeStatus(
      products[0],
      'INATIVO',
    );

    expect(
      productServiceMock.updateStatus,
    ).not.toHaveBeenCalled();
  });

  it('deletes a product after confirmation', () => {
    vi.spyOn(
      window,
      'confirm',
    ).mockReturnValue(true);

    component.deleteProduct(
      products[0],
    );

    expect(
      productServiceMock.delete,
    ).toHaveBeenCalledWith(
      products[0].id,
    );
  });

  it('removes the deleted product from the list', () => {
    vi.spyOn(
      window,
      'confirm',
    ).mockReturnValue(true);

    component.deleteProduct(
      products[0],
    );

    expect(
      component.products(),
    ).toEqual([
      products[1],
    ]);
  });

  it('shows the backend conflict message when deletion fails', () => {
    vi.spyOn(
      window,
      'confirm',
    ).mockReturnValue(true);

    productServiceMock.delete
      .mockReturnValueOnce(
        throwError(
          () => ({
            status: 409,
            error: {
              detail:
                'O produto possui variações vinculadas',
            },
          }),
        ),
      );

    component.deleteProduct(
      products[0],
    );

    expect(
      component.errorMessage(),
    ).toBe(
      'O produto possui variações vinculadas',
    );
  });

});
