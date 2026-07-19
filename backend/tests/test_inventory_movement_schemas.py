from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.inventory.movement_model import MovementType
from app.modules.inventory.movement_schemas import (
    InventoryMovementCreate,
)


def test_adjustment_accepts_zero_quantity() -> None:
    movement = InventoryMovementCreate(
        lot_id=uuid4(),
        movement_type=MovementType.ADJUSTMENT,
        quantity=Decimal("0"),
        reason="Ajuste de inventário",
    )

    assert movement.quantity == Decimal("0")


def test_adjustment_rejects_negative_quantity() -> None:
    with pytest.raises(ValueError):
        InventoryMovementCreate(
            lot_id=uuid4(),
            movement_type=MovementType.ADJUSTMENT,
            quantity=Decimal("-1"),
            reason="Ajuste inválido",
        )


@pytest.mark.parametrize(
    "movement_type",
    [
        MovementType.ENTRY,
        MovementType.RETURN,
        MovementType.LOSS,
        MovementType.SALE,
    ],
)
def test_non_adjustment_requires_positive_quantity(
    movement_type: MovementType,
) -> None:
    with pytest.raises(ValueError):
        InventoryMovementCreate(
            lot_id=uuid4(),
            movement_type=movement_type,
            quantity=Decimal("0"),
            reason="Quantidade inválida",
        )