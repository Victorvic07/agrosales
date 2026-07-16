from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.customers.customer_model import Customer
from app.modules.orders.order_model import OrderStatus
from app.modules.orders.order_schemas import OrderCreate
from app.modules.orders.order_service import OrderService


@pytest.mark.asyncio
async def test_records_draft_history_when_creating_order() -> None:
    seller_id = uuid4()
    customer_id = uuid4()

    customer = Customer(
        id=customer_id,
        name="Cliente Teste",
        document="12345678901",
        is_active=True,
    )

    order_repository = MagicMock()
    order_repository.add_order = MagicMock()
    order_repository.commit = AsyncMock()
    order_repository.refresh = AsyncMock()

    customer_repository = MagicMock()
    customer_repository.get_by_id = AsyncMock(
        return_value=customer
    )

    variation_repository = MagicMock()

    history_repository = MagicMock()
    history_repository.add = MagicMock()

    service = OrderService(
        order_repository=order_repository,
        customer_repository=customer_repository,
        variation_repository=variation_repository,
        history_repository=history_repository,
    )

    data = OrderCreate(
        customer_id=customer_id,
        notes="Pedido com histórico",
    )

    order = await service.create_order(
        data=data,
        seller_id=seller_id,
    )

    history_repository.add.assert_called_once()

    history = history_repository.add.call_args.args[0]

    assert history.order is order
    assert history.previous_status is None
    assert history.new_status == OrderStatus.DRAFT
    assert history.changed_by_user_id == seller_id

    order_repository.add_order.assert_called_once_with(order)
    order_repository.commit.assert_awaited_once()
    order_repository.refresh.assert_awaited_once_with(order)