from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot, LotStatus
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import LotCreate, LotUpdate
from app.modules.inventory.lot_service import (
    LotAlreadyExistsError,
    LotEditBlockedError,
    LotNotFoundError,
    LotService,
    LotStatusChangeBlockedError,
)
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
    variation_repository.get_by_id = AsyncMock(
        return_value=variation,
    )

    async def register_movement(**kwargs) -> None:
        movement_lot = kwargs["lot"]
        movement_lot.physical_quantity += kwargs["quantity"]

    movement_service = MagicMock()
    movement_service.register_movement = AsyncMock(
        side_effect=register_movement,
    )

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=user_id,
        movement_service=movement_service,
    )

    result = await service.create(data)

    assert result is lot
    assert lot.physical_quantity == Decimal("25")

    movement_service.register_movement.assert_awaited_once_with(
        lot=lot,
        user_id=user_id,
        movement_type=MovementType.ENTRY,
        quantity=data.initial_quantity,
        reason=data.initial_entry_reason,
        notes=data.initial_entry_notes,
        commit=False,
    )

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

@pytest.mark.asyncio
async def test_lot_service_get_returns_lot() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
    )

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)

    service = LotService(
        session=MagicMock(),
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    result = await service.get(lot_id)

    assert result is lot
    lot_repository.get_by_id.assert_awaited_once_with(lot_id)


@pytest.mark.asyncio
async def test_lot_service_get_raises_when_lot_does_not_exist() -> None:
    lot_id = uuid4()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=None)

    service = LotService(
        session=MagicMock(),
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotNotFoundError,
        match="Lote não encontrado",
    ):
        await service.get(lot_id)

@pytest.mark.asyncio
async def test_lot_service_updates_editable_lot() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("0"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)
    lot_repository.has_blocking_history = AsyncMock(
        return_value=False,
    )
    lot_repository.get_by_code_excluding_id = AsyncMock(
        return_value=None,
    )

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    new_production_date = date.today() + timedelta(days=1)
    new_expiration_date = date.today() + timedelta(days=20)

    result = await service.update(
        lot_id,
        LotUpdate(
            code="  LOTE-002  ",
            production_date=new_production_date,
            expiration_date=new_expiration_date,
        ),
    )

    assert result is lot
    assert lot.code == "LOTE-002"
    assert lot.production_date == new_production_date
    assert lot.expiration_date == new_expiration_date

    lot_repository.has_blocking_history.assert_awaited_once_with(
        lot_id,
    )
    lot_repository.get_by_code_excluding_id.assert_awaited_once_with(
        "LOTE-002",
        lot_id,
    )
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(lot)
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_lot_service_blocks_update_when_history_exists() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("0"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)
    lot_repository.has_blocking_history = AsyncMock(
        return_value=True,
    )
    lot_repository.get_by_code_excluding_id = AsyncMock()

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotEditBlockedError,
        match="histórico",
    ):
        await service.update(
            lot_id,
            LotUpdate(code="LOTE-002"),
        )

    lot_repository.get_by_code_excluding_id.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_lot_service_rejects_duplicate_code_on_update() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("0"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)
    lot_repository.has_blocking_history = AsyncMock(
        return_value=False,
    )
    lot_repository.get_by_code_excluding_id = AsyncMock(
        return_value=Lot(
            id=uuid4(),
            product_variation_id=uuid4(),
            code="LOTE-002",
        ),
    )

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotAlreadyExistsError,
        match="Já existe",
    ):
        await service.update(
            lot_id,
            LotUpdate(code="LOTE-002"),
        )

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_lot_service_blocks_inactivation_with_reservation() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("5"),
        status=LotStatus.ACTIVE,
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotStatusChangeBlockedError,
        match="reservada",
    ):
        await service.change_status(
            lot_id,
            LotStatus.INACTIVE,
        )

    assert lot.status is LotStatus.ACTIVE
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_lot_service_blocks_reactivation_of_expired_lot() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today() - timedelta(days=20),
        expiration_date=date.today() - timedelta(days=1),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("0"),
        status=LotStatus.INACTIVE,
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotStatusChangeBlockedError,
        match="vencido",
    ):
        await service.change_status(
            lot_id,
            LotStatus.ACTIVE,
        )

    assert lot.status is LotStatus.INACTIVE
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_lot_service_blocks_reactivation_without_stock() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
        status=LotStatus.INACTIVE,
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    with pytest.raises(
        LotStatusChangeBlockedError,
        match="saldo",
    ):
        await service.change_status(
            lot_id,
            LotStatus.ACTIVE,
        )

    assert lot.status is LotStatus.INACTIVE
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_lot_service_reactivates_valid_lot_with_stock() -> None:
    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("25"),
        reserved_quantity=Decimal("0"),
        status=LotStatus.INACTIVE,
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    lot_repository = MagicMock()
    lot_repository.get_by_id = AsyncMock(return_value=lot)

    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=MagicMock(),
        user_id=uuid4(),
    )

    result = await service.change_status(
        lot_id,
        LotStatus.ACTIVE,
    )

    assert result is lot
    assert lot.status is LotStatus.ACTIVE
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(lot)
    session.rollback.assert_not_awaited()