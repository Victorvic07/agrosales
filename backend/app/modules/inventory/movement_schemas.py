from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.movement_model import MovementType


class InventoryMovementCreate(BaseModel):
    lot_id: UUID
    movement_type: MovementType
    quantity: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=255)
    notes: str | None = None


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    user_id: UUID
    movement_type: MovementType
    quantity: Decimal
    previous_balance: Decimal
    new_balance: Decimal
    reason: str
    notes: str | None