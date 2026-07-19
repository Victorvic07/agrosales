import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  ProductVariation,
  ProductVariationCreate,
  ProductVariationStatusUpdate,
  ProductVariationUpdate,
} from './product-variation.models';

@Injectable({
  providedIn: 'root',
})
export class ProductVariationService {
  private readonly http = inject(HttpClient);

  private readonly baseUrl =
    '/api/v1/product-variations';

  list(): Observable<ProductVariation[]> {
    return this.http.get<ProductVariation[]>(
      this.baseUrl,
    );
  }

  create(
    data: ProductVariationCreate,
  ): Observable<ProductVariation> {
    return this.http.post<ProductVariation>(
      this.baseUrl,
      data,
    );
  }

  update(
    variationId: string,
    data: ProductVariationUpdate,
  ): Observable<ProductVariation> {
    return this.http.patch<ProductVariation>(
      `${this.baseUrl}/${variationId}`,
      data,
    );
  }

  updateStatus(
    variationId: string,
    data: ProductVariationStatusUpdate,
  ): Observable<ProductVariation> {
    return this.http.patch<ProductVariation>(
      `${this.baseUrl}/${variationId}/status`,
      data,
    );
  }
}
