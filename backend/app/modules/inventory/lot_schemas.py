from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.inventory.lot_model import ExpirationState, LotStatus


class LotCreate(BaseModel):
    product_variation_id: UUID
    code: str = Field(min_length=2, max_length=80)
    production_date: date
    expiration_date: date
    initial_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    initial_entry_reason: str | None = Field(default=None, min_length=3, max_length=255)
    initial_entry_notes: str | None = None

    @model_validator(mode="after")
    def validate_dates_and_initial_entry(self) -> "LotCreate":
        _validate_expiration_date(self.production_date, self.expiration_date)

        if self.initial_quantity > 0 and not (self.initial_entry_reason or "").strip():
            raise ValueError(
                "O motivo da entrada inicial e obrigatorio para quantidade inicial positiva"
            )

        return self


class LotUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str | None = Field(default=None, min_length=2, max_length=80)
    production_date: date | None = None
    expiration_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "LotUpdate":
        if self.expiration_date is not None:
            _validate_expiration_date(self.production_date, self.expiration_date)

        return self


class LotStatusUpdate(BaseModel):
    status: LotStatus


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_variation_id: UUID
    code: str
    production_date: date
    expiration_date: date
    physical_quantity: Decimal
    reserved_quantity: Decimal
    status: LotStatus
    available_quantity: Decimal
    expiration_state: ExpirationState
    created_at: datetime
    updated_at: datetime


def _validate_expiration_date(
    production_date: date | None,
    expiration_date: date,
) -> None:
    if expiration_date < date.today():
        raise ValueError("A data de validade nao pode ser anterior a data atual")

    if production_date is not None and expiration_date < production_date:
        raise ValueError("A data de validade nao pode ser anterior a data de producao")
