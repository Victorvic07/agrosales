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
  Product,
  ProductCreate,
  ProductStatusUpdate,
  ProductUpdate,
} from './product.models';
import {
  ProductService,
} from './product.service';

describe('ProductService', () => {
  let service: ProductService;
  let httpTesting: HttpTestingController;

  const product: Product = {
    id: 'product-1',
    category_id: null,
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
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(
      ProductService,
    );

    httpTesting = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('lists products', () => {
    service.list().subscribe(
      (products) => {
        expect(products).toEqual([
          product,
        ]);
      },
    );

    const request = httpTesting.expectOne(
      '/api/v1/products',
    );

    expect(request.request.method).toBe(
      'GET',
    );

    request.flush([
      product,
    ]);
  });

  it('creates a product', () => {
    const data: ProductCreate = {
      category_id: 'category-1',
    name: 'Tomate',
      unit: 'UNIDADE',
      cost_price: 8.5,
      standard_price: 15,
      minimum_price: 12,
    };

    service.create(data).subscribe(
      (createdProduct) => {
        expect(createdProduct).toEqual(
          product,
        );
      },
    );

    const request = httpTesting.expectOne(
      '/api/v1/products',
    );

    expect(request.request.method).toBe(
      'POST',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(product);
  });

  it('updates a product', () => {
    const data: ProductUpdate = {
      name: 'Tomate italiano',
    };

    service.update(
      product.id,
      data,
    ).subscribe(
      (updatedProduct) => {
        expect(updatedProduct).toEqual(
          product,
        );
      },
    );

    const request = httpTesting.expectOne(
      `/api/v1/products/${product.id}`,
    );

    expect(request.request.method).toBe(
      'PUT',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(product);
  });

  it('updates product status', () => {
    const data: ProductStatusUpdate = {
      status: 'DESCONTINUADO',
    };

    service.updateStatus(
      product.id,
      data,
    ).subscribe(
      (updatedProduct) => {
        expect(updatedProduct).toEqual(
          product,
        );
      },
    );

    const request = httpTesting.expectOne(
      `/api/v1/products/${product.id}/status`,
    );

    expect(request.request.method).toBe(
      'PATCH',
    );

    expect(request.request.body).toEqual(
      data,
    );

    request.flush(product);
  });

  it('uploads a product image', () => {
    const file = new File(
      [
        'image-content',
      ],
      'tomate.png',
      {
        type: 'image/png',
      },
    );

    service.uploadImage(
      product.id,
      file,
    ).subscribe(
      (updatedProduct) => {
        expect(updatedProduct).toEqual(
          product,
        );
      },
    );

    const request = httpTesting.expectOne(
      `/api/v1/products/${product.id}/image`,
    );

    expect(request.request.method).toBe(
      'POST',
    );

    expect(
      request.request.body
        instanceof FormData,
    ).toBe(true);

    const formData =
      request.request.body as FormData;

    const uploadedFile =
      formData.get('file') as File;

    expect(uploadedFile.name).toBe(
      'tomate.png',
    );

    expect(uploadedFile.type).toBe(
      'image/png',
    );

    expect(uploadedFile.size).toBe(
      file.size,
    );

    request.flush(product);
  });

  it('removes a product image', () => {
    service.removeImage(
      product.id,
    ).subscribe(
      (updatedProduct) => {
        expect(updatedProduct).toEqual(
          product,
        );
      },
    );

    const request = httpTesting.expectOne(
      `/api/v1/products/${product.id}/image`,
    );

    expect(request.request.method).toBe(
      'DELETE',
    );

    request.flush(product);
  });

  it('deletes a product', () => {
    service.delete(
      product.id,
    ).subscribe();

    const request = httpTesting.expectOne(
      `/api/v1/products/${product.id}`,
    );

    expect(request.request.method).toBe(
      'DELETE',
    );

    request.flush(null);
  });

  it('builds the product image URL', () => {
    const productWithImage: Product = {
      ...product,
      image_path:
        'products/PRD-000001-image.webp',
    };

    expect(
      service.imageUrl(
        productWithImage,
      ),
    ).toBe(
      '/uploads/products/PRD-000001-image.webp',
    );
  });

  it('returns null when product has no image', () => {
    expect(
      service.imageUrl(product),
    ).toBeNull();
  });
});