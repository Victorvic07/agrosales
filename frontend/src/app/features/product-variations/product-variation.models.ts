export interface ProductVariation {
  id: string;
  product_id: string;
  internal_code: string;
  classification: string | null;
  package_type: string;
  unit_of_measure: string;
  weight_or_volume: string | null;
  standard_price: string;
  minimum_price: string;
  minimum_stock: string;
  commission_percentage: string;
  barcode: string | null;
  qr_code: string | null;
  is_active: boolean;
}

export interface ProductVariationCreate {
  product_id: string;
  internal_code: string;
  classification: string | null;
  package_type: string;
  unit_of_measure: string;
  weight_or_volume: number | null;
  standard_price: number;
  minimum_price: number;
  minimum_stock: number;
  commission_percentage: number;
  barcode: string | null;
  qr_code: string | null;
}

export type ProductVariationUpdate = Omit<
  ProductVariationCreate,
  'product_id' | 'internal_code'
>;

export interface ProductVariationStatusUpdate {
  is_active: boolean;
}
