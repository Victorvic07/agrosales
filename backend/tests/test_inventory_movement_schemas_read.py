from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.core.enums import UserRole
from app.modules.inventory.movement_model import (
    InventoryMovement,
    MovementType,
)
from app.modules.inventory.movement_schemas import (
    InventoryMovementRead,
)
from app.modules.users.model import User


def test_movement_read_contains_user_and_date() -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    created_at = datetime.now(UTC)

    movement = InventoryMovement(
        id=uuid4(),
        lot_id=uuid4(),
        user_id=user.id,
        movement_type=MovementType.ENTRY,
        quantity=Decimal("10"),
        previous_balance=Decimal("0"),
        new_balance=Decimal("10"),
        reason="Entrada",
        notes=None,
        created_at=created_at,
    )
    movement.user = user

    result = InventoryMovementRead.model_validate(movement)

    assert result.user_name == "Produtor"
    assert result.created_at == created_at