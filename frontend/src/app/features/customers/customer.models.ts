export type CustomerType =
  | 'INDIVIDUAL'
  | 'COMPANY';

export type DocumentType =
  | 'CPF'
  | 'CNPJ';

export interface Customer {
  id: string;
  customer_type: CustomerType;
  document_type: DocumentType;
  document: string;
  name: string;
  phone: string | null;
  email: string | null;
  street: string | null;
  number: string | null;
  complement: string | null;
  neighborhood: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type CustomerCreate = Omit<
  Customer,
  | 'id'
  | 'is_active'
  | 'created_at'
  | 'updated_at'
>;

export type CustomerUpdate =
  Partial<CustomerCreate>;

export interface CustomerStatusUpdate {
  is_active: boolean;
}
