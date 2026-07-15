from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_service import (
    InsufficientAvailableStockError,
)
from app.modules.orders.order_confirmation_service import (
    OrderConfirmationService,
    OrderWithoutItemsError,
)
from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import Order, OrderStatus


def create_lot(
    quantity: str,
    expiration_date: date,
) -> Lot:
    return Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code=f"LOTE-{uuid4()}",
        production_date=date(2026, 7, 1),
        expiration_date=expiration_date,
        physical_quantity=Decimal(quantity),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )


@pytest.mark.asyncio
async def test_confirms_order_and_creates_reservation() -> None:
    variation_id = uuid4()

    item = OrderItem(
        id=uuid4(),
        order_id=uuid4(),
        product_variation_id=variation_id,
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("1000"),
    )

    order = Order(
        id=item.order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("1000"),
        discount_total=Decimal("0"),
        total_amount=Decimal("1000"),
    )
    order.items = [item]

    lot = create_lot(
        quantity="20",
        expiration_date=date(2026, 8, 1),
    )
    lot.product_variation_id = variation_id

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
        return_value=[lot]
    )

    service = OrderConfirmationService(
        session=session,
        order_repository=order_repository,
        customer_repository=customer_repository,
        reservation_repository=reservation_repository,
    )

    result = await service.confirm(
        order_id=order.id,
        reference_date=date(2026, 7, 15),
    )

    assert result.status == OrderStatus.CONFIRMED
    assert result.confirmed_at is not None
    assert lot.reserved_quantity == Decimal("10")
    assert reservation_repository.add.call_count == 1

    created_reservation = (
        reservation_repository.add.call_args.args[0]
    )

    assert created_reservation.order_item_id == item.id
    assert created_reservation.quantity == Decimal("10")

    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_order_without_items() -> None:
    order = Order(
        id=uuid4(),
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("0"),
        discount_total=Decimal("0"),
        total_amount=Decimal("0"),
    )
    order.items = []

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    order_repository = MagicMock()
    order_repository.get_by_id_for_update = AsyncMock(
        return_value=order
    )

    service = OrderConfirmationService(
        session=session,
        order_repository=order_repository,
        customer_repository=MagicMock(),
        reservation_repository=MagicMock(),
    )

    with pytest.raises(OrderWithoutItemsError):
        await service.confirm(order.id)

    assert order.status == OrderStatus.DRAFT
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_rolls_back_when_stock_is_insufficient() -> None:
    variation_id = uuid4()

    item = OrderItem(
        id=uuid4(),
        order_id=uuid4(),
        product_variation_id=variation_id,
        quantity=Decimal("50"),
        unit_price=Decimal("100"),
        discount_amount=Decimal("0"),
        total_amount=Decimal("5000"),
    )

    order = Order(
        id=item.order_id,
        customer_id=uuid4(),
        seller_id=uuid4(),
        status=OrderStatus.DRAFT,
        subtotal=Decimal("5000"),
        discount_total=Decimal("0"),
        total_amount=Decimal("5000"),
    )
    order.items = [item]

    lot = create_lot(
        quantity="10",
        expiration_date=date(2026, 8, 1),
    )
    lot.product_variation_id = variation_id

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

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
        return_value=[lot]
    )

    service = OrderConfirmationService(
        session=session,
        order_repository=order_repository,
        customer_repository=customer_repository,
        reservation_repository=reservation_repository,
    )

    with pytest.raises(
        InsufficientAvailableStockError
    ):
        await service.confirm(
            order_id=order.id,
            reference_date=date(2026, 7, 15),
        )

    assert order.status == OrderStatus.DRAFT
    assert lot.reserved_quantity == Decimal("0")

    reservation_repository.add.assert_not_called()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()