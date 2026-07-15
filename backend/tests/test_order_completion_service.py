from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.orders.order_completion_service import (
    InvalidStockBalanceError,
    OrderCannotBeCompletedError,
    OrderCompletionService,
    OrderNotFoundError,
)
from app.modules.orders.order_model import Order, OrderStatus


@pytest.mark.asyncio
async def test_completes_confirmed_order_and_consumes_reservation() -> None:
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

    service = OrderCompletionService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    result = await service.complete(order.id)

    assert result.status == OrderStatus.COMPLETED
    assert result.completed_at is not None

    assert reservation.status == ReservationStatus.CONSUMED

    assert lot.physical_quantity == Decimal("90")
    assert lot.reserved_quantity == Decimal("10")

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_unknown_order() -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=None
    )

    reservation_repository = MagicMock()
    reservation_repository.list_active_by_order = AsyncMock()

    service = OrderCompletionService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    with pytest.raises(
        OrderNotFoundError,
        match="Pedido não encontrado",
    ):
        await service.complete(uuid4())

    reservation_repository.list_active_by_order.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_rejects_order_that_is_not_confirmed() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
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

    service = OrderCompletionService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    with pytest.raises(
        OrderCannotBeCompletedError,
        match="Apenas pedidos confirmados podem ser concluídos",
    ):
        await service.complete(order.id)

    reservation_repository.list_active_by_order.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_rolls_back_when_stock_balance_is_inconsistent() -> None:
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
        physical_quantity=Decimal("5"),
        reserved_quantity=Decimal("10"),
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

    service = OrderCompletionService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
    )

    with pytest.raises(
        InvalidStockBalanceError,
        match="Saldo de estoque do lote está inconsistente",
    ):
        await service.complete(order.id)

    assert order.status == OrderStatus.CONFIRMED
    assert reservation.status == ReservationStatus.ACTIVE
    assert lot.physical_quantity == Decimal("5")
    assert lot.reserved_quantity == Decimal("10")

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()