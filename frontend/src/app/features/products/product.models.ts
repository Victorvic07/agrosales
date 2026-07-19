export interface Category {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
}

export type ProductUnit =
  | 'UNIDADE'
  | 'QUILOGRAMA'
  | 'GRAMA'
  | 'LITRO'
  | 'MILILITRO'
  | 'CAIXA'
  | 'PACOTE'
  | 'SACO'
  | 'OUTRO';

export type ProductStatus =
  | 'ATIVO'
  | 'INATIVO'
  | 'DESCONTINUADO';

export interface Product {
  id: string;
  category_id: string | null;
  code: string;
  name: string;
  unit: ProductUnit;
  custom_unit: string | null;
  cost_price: string;
  standard_price: string;
  minimum_price: string;
  short_description: string | null;
  detailed_description: string | null;
  internal_notes: string | null;
  image_path: string | null;
  status: ProductStatus;
}

export interface ProductCreate {
  category_id: string;
  code?: string | null;
  name: string;
  unit: ProductUnit;
  custom_unit?: string | null;
  cost_price: number;
  standard_price: number;
  minimum_price: number;
  short_description?: string | null;
  detailed_description?: string | null;
  internal_notes?: string | null;
}

export type ProductUpdate =
  Partial<ProductCreate>;

export interface ProductStatusUpdate {
  status: ProductStatus;
}
