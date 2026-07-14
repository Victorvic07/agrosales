from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.movement_model import MovementType
from app.modules.inventory.movement_service import (
    InsufficientStockError,
    InventoryMovementService,
)


@pytest.mark.asyncio
async def test_entry_increases_lot_balance() -> None:
    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = InventoryMovementService(session)

    movement = await service.register_movement(
        lot=lot,
        user_id=uuid4(),
        movement_type=MovementType.ENTRY,
        quantity=Decimal("50"),
        reason="Entrada de produção",
    )

    assert lot.physical_quantity == Decimal("150")
    assert movement.previous_balance == Decimal("100")
    assert movement.new_balance == Decimal("150")


@pytest.mark.asyncio
async def test_loss_decreases_lot_balance() -> None:
    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = InventoryMovementService(session)

    movement = await service.register_movement(
        lot=lot,
        user_id=uuid4(),
        movement_type=MovementType.LOSS,
        quantity=Decimal("10"),
        reason="Produto avariado",
    )

    assert lot.physical_quantity == Decimal("90")
    assert movement.new_balance == Decimal("90")


@pytest.mark.asyncio
async def test_movement_cannot_reduce_below_reserved_quantity() -> None:
    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("80"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = InventoryMovementService(session)

    with pytest.raises(
        InsufficientStockError,
        match="abaixo da quantidade reservada",
    ):
        await service.register_movement(
            lot=lot,
            user_id=uuid4(),
            movement_type=MovementType.LOSS,
            quantity=Decimal("30"),
            reason="Produto avariado",
        )


@pytest.mark.asyncio
async def test_sale_cannot_create_negative_stock() -> None:
    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("20"),
        reserved_quantity=Decimal("0"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = InventoryMovementService(session)

    with pytest.raises(
        InsufficientStockError,
        match="Quantidade insuficiente",
    ):
        await service.register_movement(
            lot=lot,
            user_id=uuid4(),
            movement_type=MovementType.SALE,
            quantity=Decimal("30"),
            reason="Baixa por venda",
        )