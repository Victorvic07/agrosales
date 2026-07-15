from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_application_service import (
    ProductVariationNotFoundError,
    ReservationApplicationService,
)
from app.modules.inventory.reservation_service import (
    InsufficientAvailableStockError,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationRequest,
)
from app.modules.products.variation_model import ProductVariation


def make_lot(
    code: str,
    expiration_date: date,
    quantity: str,
) -> Lot:
    return Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code=code,
        production_date=date(2026, 7, 1),
        expiration_date=expiration_date,
        physical_quantity=Decimal(quantity),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )


@pytest.mark.asyncio
async def test_service_creates_split_fefo_reservation() -> None:
    variation_id = uuid4()

    variation = ProductVariation(
        id=variation_id,
        product_id=uuid4(),
        internal_code="TOM-ITA-20-A",
        package_type="Caixa",
        unit_of_measure="CAIXA",
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        is_active=True,
    )

    first_lot = make_lot(
        code="LOTE-001",
        expiration_date=date(2026, 7, 20),
        quantity="30",
    )

    second_lot = make_lot(
        code="LOTE-002",
        expiration_date=date(2026, 7, 30),
        quantity="80",
    )

    first_lot.product_variation_id = variation_id
    second_lot.product_variation_id = variation_id

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def refresh_reservation(reservation) -> None:
        reservation.id = uuid4()

    session.refresh = AsyncMock(
        side_effect=refresh_reservation
    )

    reservation_repository = MagicMock()
    reservation_repository.get_eligible_lots = AsyncMock(
        return_value=[
            first_lot,
            second_lot,
        ]
    )

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=variation
    )

    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    result = await service.create(
        StockReservationRequest(
            product_variation_id=variation_id,
            quantity=Decimal("50"),
        ),
        reference_date=date(2026, 7, 15),
    )

    assert result.reserved_quantity == Decimal("50")

    assert [
        allocation.quantity
        for allocation in result.allocations
    ] == [
        Decimal("30"),
        Decimal("20"),
    ]

    assert first_lot.reserved_quantity == Decimal("30")
    assert second_lot.reserved_quantity == Decimal("20")

    assert reservation_repository.add.call_count == 2

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_service_rolls_back_when_stock_is_insufficient() -> None:
    variation_id = uuid4()

    variation = MagicMock(
        is_active=True
    )

    lot = make_lot(
        code="LOTE-001",
        expiration_date=date(2026, 7, 20),
        quantity="10",
    )

    lot.product_variation_id = variation_id

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    reservation_repository = MagicMock()
    reservation_repository.get_eligible_lots = AsyncMock(
        return_value=[lot]
    )

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=variation
    )

    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    with pytest.raises(
        InsufficientAvailableStockError
    ):
        await service.create(
            StockReservationRequest(
                product_variation_id=variation_id,
                quantity=Decimal("50"),
            ),
            reference_date=date(2026, 7, 15),
        )

    assert lot.reserved_quantity == Decimal("0")

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_rejects_inactive_variation() -> None:
    session = MagicMock()
    session.rollback = AsyncMock()

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=MagicMock(
            is_active=False
        )
    )

    service = ReservationApplicationService(
        session=session,
        reservation_repository=MagicMock(),
        variation_repository=variation_repository,
    )

    with pytest.raises(
        ProductVariationNotFoundError
    ):
        await service.create(
            StockReservationRequest(
                product_variation_id=uuid4(),
                quantity=Decimal("10"),
            )
        )

    session.rollback.assert_awaited_once()