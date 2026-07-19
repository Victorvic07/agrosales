from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.modules.inventory.movement_model import MovementType


class InventoryMovementCreate(BaseModel):
    lot_id: UUID
    movement_type: MovementType
    quantity: Decimal = Field()
    reason: str = Field(min_length=3, max_length=255)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_quantity(self) -> "InventoryMovementCreate":
        if self.movement_type == MovementType.ADJUSTMENT:
            if self.quantity < 0:
                raise ValueError(
                    "Ajuste não pode possuir quantidade negativa."
                )

        elif self.quantity <= 0:
            raise ValueError(
                "A quantidade deve ser maior que zero."
            )

        return self


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    user_id: UUID
    user_name: str
    movement_type: MovementType
    quantity: Decimal
    previous_balance: Decimal
    new_balance: Decimal
    reason: str
    notes: str | None
    created_at: datetime