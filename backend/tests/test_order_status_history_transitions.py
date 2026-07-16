from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.reservation_model import (
    ReservationStatus,
)
from app.modules.orders.order_cancellation_service import (
    OrderCancellationService,
)
from app.modules.orders.order_confirmation_service import (
    OrderConfirmationService,
)
from app.modules.orders.order_model import Order, OrderStatus
from app.modules.orders.order_completion_service import (
    OrderCompletionService,
)


@pytest.mark.asyncio
async def test_records_confirmation_history() -> None:
    user_id = uuid4()

    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("100"),
        discount_total=Decimal("0"),
        total_amount=Decimal("100"),
    )

    order.items = [MagicMock()]

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    customer_repository = MagicMock()
    customer_repository.get_by_id = AsyncMock(
        return_value=MagicMock(is_active=True)
    )

    reservation_repository = MagicMock()
    reservation_repository.get_eligible_lots = AsyncMock(
        return_value=[]
    )

    history_repository = MagicMock()
    history_repository.add = MagicMock()

    service = OrderConfirmationService(
        session=session,
        order_repository=order_repository,
        customer_repository=customer_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    with pytest.raises(Exception):
        await service.confirm(
            order.id,
            changed_by_user_id=user_id,
        )


@pytest.mark.asyncio
async def test_records_cancellation_history() -> None:
    user_id = uuid4()

    lot = MagicMock()
    lot.reserved_quantity = Decimal("10")

    reservation = MagicMock()
    reservation.quantity = Decimal("4")
    reservation.status = ReservationStatus.ACTIVE
    reservation.lot = lot

    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
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
    reservation_repository.list_active_by_order = AsyncMock(
        return_value=[reservation]
    )

    history_repository = MagicMock()
    history_repository.add = MagicMock()

    service = OrderCancellationService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    result = await service.cancel(
        order.id,
        changed_by_user_id=user_id,
    )

    assert result is order
    assert order.status == OrderStatus.CANCELLED
    assert lot.reserved_quantity == Decimal("6")
    assert reservation.status == ReservationStatus.RELEASED

    history_repository.add.assert_called_once()

    history = history_repository.add.call_args.args[0]

    assert history.order is order
    assert history.previous_status == OrderStatus.CONFIRMED
    assert history.new_status == OrderStatus.CANCELLED
    assert history.changed_by_user_id == user_id

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(order)


@pytest.mark.asyncio
async def test_records_completion_history() -> None:
    user_id = uuid4()

    lot = MagicMock()
    lot.physical_quantity = Decimal("10")
    lot.reserved_quantity = Decimal("4")

    reservation = MagicMock()
    reservation.quantity = Decimal("4")
    reservation.status = ReservationStatus.ACTIVE
    reservation.lot = lot

    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.CONFIRMED,
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
    reservation_repository.list_active_by_order = AsyncMock(
        return_value=[reservation]
    )

    history_repository = MagicMock()
    history_repository.add = MagicMock()

    service = OrderCompletionService(
        session=session,
        order_repository=order_repository,
        reservation_repository=reservation_repository,
        history_repository=history_repository,
    )

    result = await service.complete(
        order.id,
        changed_by_user_id=user_id,
    )

    assert result is order
    assert order.status == OrderStatus.COMPLETED
    assert lot.physical_quantity == Decimal("6")
    assert lot.reserved_quantity == Decimal("0")
    assert reservation.status == ReservationStatus.CONSUMED

    history_repository.add.assert_called_once()

    history = history_repository.add.call_args.args[0]

    assert history.order is order
    assert history.previous_status == OrderStatus.CONFIRMED
    assert history.new_status == OrderStatus.COMPLETED
    assert history.changed_by_user_id == user_id

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(order)
