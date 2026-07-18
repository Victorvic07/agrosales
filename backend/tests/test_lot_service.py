from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import LotCreate
from app.modules.inventory.lot_service import LotService
from app.modules.inventory.movement_model import MovementType
from app.modules.products.variation_model import ProductVariation


def build_lot_create() -> LotCreate:
    return LotCreate(
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        initial_quantity=Decimal("25"),
        initial_entry_reason="Colheita inicial",
        initial_entry_notes="Primeira entrada do lote",
    )


@pytest.mark.asyncio
async def test_lot_repository_creates_empty_lot_without_committing() -> None:
    session = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    repository = LotRepository(session)

    lot = await repository.create(build_lot_create())

    assert lot.physical_quantity == Decimal("0")
    assert lot.reserved_quantity == Decimal("0")
    session.flush.assert_awaited_once()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_lot_service_creates_initial_entry_in_one_transaction() -> None:
    data = build_lot_create()
    user_id = uuid4()
    lot = Lot(
        id=uuid4(),
        product_variation_id=data.product_variation_id,
        code=data.code,
        production_date=data.production_date,
        expiration_date=data.expiration_date,
        physical_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
    )
    variation = ProductVariation(
        id=data.product_variation_id,
        product_id=uuid4(),
        internal_code="TOM-001",
        package_type="Caixa",
        unit_of_measure="CAIXA",
        standard_price=Decimal("10"),
        minimum_price=Decimal("8"),
        is_active=True,
    )
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    lot_repository = MagicMock()
    lot_repository.get_by_code = AsyncMock(return_value=None)
    lot_repository.create = AsyncMock(return_value=lot)
    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(return_value=variation)

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=user_id,
    )

    result = await service.create(data)

    movement = session.add.call_args.args[0]
    assert result is lot
    assert lot.physical_quantity == Decimal("25")
    assert movement.user_id == user_id
    assert movement.movement_type is MovementType.ENTRY
    assert movement.reason == data.initial_entry_reason
    assert movement.notes == data.initial_entry_notes
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(lot)


@pytest.mark.asyncio
async def test_lot_service_rolls_back_when_creation_fails() -> None:
    data = build_lot_create()
    session = MagicMock()
    session.rollback = AsyncMock()
    lot_repository = MagicMock()
    lot_repository.get_by_code = AsyncMock(return_value=None)
    lot_repository.create = AsyncMock(side_effect=RuntimeError("database failed"))
    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=MagicMock(is_active=True)
    )
    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=uuid4(),
    )

    with pytest.raises(RuntimeError, match="database failed"):
        await service.create(data)

    session.rollback.assert_awaited_once()
