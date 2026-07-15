from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.orders.order_cancellation_service import (
    InvalidReservedStockError,
    OrderCancellationService,
    OrderCannotBeCancelledError,
)
from app.modules.orders.order_model import Order, OrderStatus


@pytest.mark.asyncio
async def test_cancels_draft_order_without_touching_stock() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("0"),
        discount_total=Decimal("0"),
        total_amount=Decimal("0"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    reservation_repository = MagicMock()
    reservation_repository.list_active_by_order = AsyncMock()

    service = OrderCancellationService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    result = await service.cancel(order.id)

    assert result.status == OrderStatus.CANCELLED
    assert result.cancelled_at is not None
    reservation_repository.list_active_by_order.assert_not_awaited()
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancels_confirmed_order_and_releases_reservation() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
    )

    reservation = StockReservation(
        id=uuid4(),
        lot_id=lot.id,
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )
    reservation.lot = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    reservation_repository = MagicMock()
    reservation_repository.list_active_by_order = AsyncMock(
        return_value=[reservation]
    )

    service = OrderCancellationService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    result = await service.cancel(order.id)

    assert result.status == OrderStatus.CANCELLED
    assert reservation.status == ReservationStatus.RELEASED
    assert lot.reserved_quantity == Decimal("10")
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_completed_order() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.COMPLETED,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    service = OrderCancellationService(
        session=session,
        order_repository=order_repository,
        reservation_repository=MagicMock(),
    )

    with pytest.raises(OrderCannotBeCancelledError):
        await service.cancel(order.id)

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_rolls_back_when_reserved_stock_is_inconsistent() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("5"),
    )

    reservation = StockReservation(
        id=uuid4(),
        lot_id=lot.id,
        quantity=Decimal("10"),
        status=ReservationStatus.ACTIVE,
    )
    reservation.lot = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    reservation_repository = MagicMock()
    reservation_repository.list_active_by_order = AsyncMock(
        return_value=[reservation]
    )

    service = OrderCancellationService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    with pytest.raises(InvalidReservedStockError):
        await service.cancel(order.id)

    assert order.status == OrderStatus.CONFIRMED
    assert reservation.status == ReservationStatus.ACTIVE
    assert lot.reserved_quantity == Decimal("5")
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()