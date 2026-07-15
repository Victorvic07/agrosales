from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.reservation_model import ReservationStatus


class StockReservationCreate(BaseModel):
    lot_id: UUID
    quantity: Decimal = Field(gt=0)


class StockReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    order_item_id: UUID | None
    quantity: Decimal
    status: ReservationStatus


class StockReservationRequest(BaseModel):
    product_variation_id: UUID
    quantity: Decimal = Field(gt=0)


class StockReservationAllocationRead(BaseModel):
    reservation_id: UUID
    lot_id: UUID
    lot_code: str
    quantity: Decimal
    expiration_date: date


class StockReservationSummaryRead(BaseModel):
    product_variation_id: UUID
    requested_quantity: Decimal
    reserved_quantity: Decimal
    allocations: list[StockReservationAllocationRead]