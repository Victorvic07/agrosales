from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LotCreate(BaseModel):
    product_variation_id: UUID
    code: str = Field(min_length=2, max_length=80)
    production_date: date
    expiration_date: date
    physical_quantity: Decimal = Field(default=0, ge=0)
    reserved_quantity: Decimal = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_dates_and_quantities(self):
        if self.expiration_date < self.production_date:
            raise ValueError(
                "A data de validade não pode ser anterior à data de produção"
            )

        if self.reserved_quantity > self.physical_quantity:
            raise ValueError(
                "A quantidade reservada não pode ser maior que a quantidade física"
            )

        return self


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_variation_id: UUID
    code: str
    production_date: date
    expiration_date: date
    physical_quantity: Decimal
    reserved_quantity: Decimal
    status: str