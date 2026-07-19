import {
  HttpClient,
} from '@angular/common/http';
import {
  inject,
  Injectable,
} from '@angular/core';
import {
  Observable,
} from 'rxjs';

import {
  InventoryMovement,
  InventoryMovementCreate,
  Lot,
  LotCreate,
  LotStatusUpdate,
  LotUpdate,
} from './lot.models';

@Injectable({
  providedIn: 'root',
})
export class LotService {
  private readonly http = inject(HttpClient);

  private readonly lotsUrl =
    '/api/v1/lots';

  private readonly movementsUrl =
    '/api/v1/inventory-movements';

  list(): Observable<Lot[]> {
    return this.http.get<Lot[]>(
      this.lotsUrl,
    );
  }

  get(
    lotId: string,
  ): Observable<Lot> {
    return this.http.get<Lot>(
      `${this.lotsUrl}/${lotId}`,
    );
  }

  create(
    data: LotCreate,
  ): Observable<Lot> {
    return this.http.post<Lot>(
      this.lotsUrl,
      data,
    );
  }

  update(
    lotId: string,
    data: LotUpdate,
  ): Observable<Lot> {
    return this.http.put<Lot>(
      `${this.lotsUrl}/${lotId}`,
      data,
    );
  }

  updateStatus(
    lotId: string,
    data: LotStatusUpdate,
  ): Observable<Lot> {
    return this.http.patch<Lot>(
      `${this.lotsUrl}/${lotId}/status`,
      data,
    );
  }

  listMovements(
    lotId: string,
  ): Observable<InventoryMovement[]> {
    return this.http.get<
      InventoryMovement[]
    >(
      `${this.movementsUrl}?lot_id=${lotId}`,
    );
  }

  createMovement(
    data: InventoryMovementCreate,
  ): Observable<InventoryMovement> {
    return this.http.post<
      InventoryMovement
    >(
      this.movementsUrl,
      data,
    );
  }
}