import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  Category,
  Product,
  ProductCreate,
  ProductStatusUpdate,
  ProductUpdate,
} from './product.models';

@Injectable({
  providedIn: 'root',
})
export class ProductService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1/products';
  private readonly categoriesUrl = '/api/v1/categories';

  listCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(
      this.categoriesUrl,
    );
  }

  list(): Observable<Product[]> {
    return this.http.get<Product[]>(
      this.apiUrl,
    );
  }

  create(
    data: ProductCreate,
  ): Observable<Product> {
    return this.http.post<Product>(
      this.apiUrl,
      data,
    );
  }

  update(
    id: string,
    data: ProductUpdate,
  ): Observable<Product> {
    return this.http.put<Product>(
      `${this.apiUrl}/${id}`,
      data,
    );
  }

  updateStatus(
    id: string,
    data: ProductStatusUpdate,
  ): Observable<Product> {
    return this.http.patch<Product>(
      `${this.apiUrl}/${id}/status`,
      data,
    );
  }

  uploadImage(
    id: string,
    file: File,
  ): Observable<Product> {
    const formData = new FormData();
    formData.append(
      'file',
      file,
      file.name,
    );

    return this.http.post<Product>(
      `${this.apiUrl}/${id}/image`,
      formData,
    );
  }

  removeImage(
    id: string,
  ): Observable<Product> {
    return this.http.delete<Product>(
      `${this.apiUrl}/${id}/image`,
    );
  }

  delete(
    id: string,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/${id}`,
    );
  }

  imageUrl(
    product: Product,
  ): string | null {
    if (!product.image_path) {
      return null;
    }

    return `/uploads/${product.image_path}`;
  }
}
