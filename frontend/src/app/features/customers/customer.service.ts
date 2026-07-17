import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  Customer,
  CustomerCreate,
  CustomerStatusUpdate,
  CustomerUpdate,
} from './customer.models';

@Injectable({
  providedIn: 'root',
})
export class CustomerService {
  private readonly http = inject(HttpClient);

  private readonly baseUrl =
    '/api/v1/customers';

  list(): Observable<Customer[]> {
    return this.http.get<Customer[]>(
      `${this.baseUrl}?include_inactive=true`,
    );
  }

  create(
    data: CustomerCreate,
  ): Observable<Customer> {
    return this.http.post<Customer>(
      this.baseUrl,
      data,
    );
  }

  update(
    customerId: string,
    data: CustomerUpdate,
  ): Observable<Customer> {
    return this.http.patch<Customer>(
      `${this.baseUrl}/${customerId}`,
      data,
    );
  }

  updateStatus(
    customerId: string,
    data: CustomerStatusUpdate,
  ): Observable<Customer> {
    return this.http.patch<Customer>(
      `${this.baseUrl}/${customerId}/status`,
      data,
    );
  }
}
