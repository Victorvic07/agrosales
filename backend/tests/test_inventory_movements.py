from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.movement_model import (
    InventoryMovement,
    MovementType,
)
from app.modules.inventory.movement_schemas import InventoryMovementCreate


def test_inventory_movement_table_name() -> None:
    assert InventoryMovement.__tablename__ == "inventory_movements"


def test_movement_types_are_correct() -> None:
    assert {movement.value for movement in MovementType} == {
        "ENTRY",
        "SALE",
        "LOSS",
        "RETURN",
        "ADJUSTMENT",
    }


def test_inventory_movement_accepts_valid_quantity() -> None:
    movement = InventoryMovementCreate(
        lot_id=uuid4(),
        movement_type=MovementType.ENTRY,
        quantity=Decimal("100"),
        reason="Entrada de produção",
    )

    assert movement.quantity == Decimal("100")


def test_inventory_movement_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        InventoryMovementCreate(
            lot_id=uuid4(),
            movement_type=MovementType.LOSS,
            quantity=Decimal("0"),
            reason="Produto avariado",
        )