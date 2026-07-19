export type LotStatus =
  | 'ACTIVE'
  | 'INACTIVE';

export type ExpirationState =
  | 'EXPIRED'
  | 'EXPIRES_TODAY'
  | 'EXPIRING_SOON'
  | 'REGULAR';

export type MovementType =
  | 'ENTRY'
  | 'SALE'
  | 'LOSS'
  | 'RETURN'
  | 'ADJUSTMENT';

export type ManualMovementType =
  Exclude<MovementType, 'SALE'>;

export interface Lot {
  id: string;
  product_variation_id: string;
  code: string;
  production_date: string;
  expiration_date: string;
  physical_quantity: string;
  reserved_quantity: string;
  available_quantity: string;
  status: LotStatus;
  expiration_state: ExpirationState;
  created_at: string;
  updated_at: string;
}

export interface LotCreate {
  product_variation_id: string;
  code: string;
  production_date: string;
  expiration_date: string;
  initial_quantity: number;
  initial_entry_reason: string | null;
  notes: string | null;
}

export interface LotUpdate {
  code: string;
  production_date: string;
  expiration_date: string;
}

export interface LotStatusUpdate {
  status: LotStatus;
}

export interface InventoryMovement {
  id: string;
  lot_id: string;
  user_id: string;
  user_name: string;
  movement_type: MovementType;
  quantity: string;
  previous_balance: string;
  new_balance: string;
  reason: string;
  notes: string | null;
  created_at: string;
}

export interface InventoryMovementCreate {
  lot_id: string;
  movement_type: ManualMovementType;
  quantity: number;
  reason: string;
  notes: string | null;
}