from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.enums import UserRole
from app.modules.orders.order_model import Order, OrderStatus
from app.modules.orders.order_schemas import (
    OrderCreate,
    OrderItemCreate,
)
from app.modules.orders.order_service import (
    InactiveCustomerError,
    OrderService,
    PriceBelowMinimumError,
)


@pytest.mark.asyncio
async def test_service_rejects_inactive_customer() -> None:
    customer_repository = MagicMock()
    customer_repository.get_by_id = AsyncMock(
        return_value=MagicMock(is_active=False)
    )

    service = OrderService(
        order_repository=MagicMock(),
        customer_repository=customer_repository,
        variation_repository=MagicMock(),
    )

    with pytest.raises(InactiveCustomerError):
        await service.create_order(
            data=OrderCreate(
                customer_id=uuid4(),
            ),
            seller_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_service_rejects_price_below_minimum_for_vendor() -> None:
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

    order_repository = MagicMock()
    order_repository.get_by_id = AsyncMock(
        return_value=order
    )
    order_repository.get_item_by_variation = AsyncMock(
        return_value=None
    )

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=MagicMock(
            is_active=True,
            standard_price=Decimal("100"),
            minimum_price=Decimal("90"),
        )
    )

    service = OrderService(
        order_repository=order_repository,
        customer_repository=MagicMock(),
        variation_repository=variation_repository,
    )

    with pytest.raises(PriceBelowMinimumError):
        await service.add_item(
            order_id=order.id,
            data=OrderItemCreate(
                product_variation_id=uuid4(),
                quantity=Decimal("1"),
                unit_price=Decimal("80"),
            ),
            user_role=UserRole.VENDEDOR,
        )


@pytest.mark.asyncio
async def test_service_allows_admin_price_below_minimum() -> None:
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

    order_repository = MagicMock()
    order_repository.get_by_id = AsyncMock(
        return_value=order
    )
    order_repository.get_item_by_variation = AsyncMock(
        return_value=None
    )
    order_repository.commit = AsyncMock()
    order_repository.refresh = AsyncMock()

    variation_repository = MagicMock()
    variation_repository.get_by_id = AsyncMock(
        return_value=MagicMock(
            is_active=True,
            standard_price=Decimal("100"),
            minimum_price=Decimal("90"),
        )
    )

    service = OrderService(
        order_repository=order_repository,
        customer_repository=MagicMock(),
        variation_repository=variation_repository,
    )

    item = await service.add_item(
        order_id=order.id,
        data=OrderItemCreate(
            product_variation_id=uuid4(),
            quantity=Decimal("2"),
            unit_price=Decimal("80"),
            discount_amount=Decimal("10"),
        ),
        user_role=UserRole.ADMINISTRADOR,
    )

    assert item.total_amount == Decimal("150")
    assert order.subtotal == Decimal("160")
    assert order.discount_total == Decimal("10")
    assert order.total_amount == Decimal("150")