from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductVariationCreate(BaseModel):
    product_id: UUID
    internal_code: str = Field(min_length=2, max_length=50)
    classification: str | None = Field(default=None, max_length=100)
    package_type: str = Field(min_length=2, max_length=100)
    unit_of_measure: str = Field(min_length=1, max_length=30)
    weight_or_volume: Decimal | None = Field(default=None, gt=0)
    standard_price: Decimal = Field(gt=0)
    minimum_price: Decimal = Field(gt=0)
    minimum_stock: Decimal = Field(default=0, ge=0)
    commission_percentage: Decimal = Field(default=0, ge=0, le=100)
    barcode: str | None = Field(default=None, max_length=100)
    qr_code: str | None = Field(default=None, max_length=255)


class ProductVariationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    internal_code: str
    classification: str | None
    package_type: str
    unit_of_measure: str
    weight_or_volume: Decimal | None
    standard_price: Decimal
    minimum_price: Decimal
    minimum_stock: Decimal
    commission_percentage: Decimal
    barcode: str | None
    qr_code: str | None
    is_active: bool