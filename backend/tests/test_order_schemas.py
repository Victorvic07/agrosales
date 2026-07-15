from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.orders.order_schemas import (
    OrderCreate,
    OrderItemCreate,
)


def test_order_create_accepts_customer_and_notes() -> None:
    payload = OrderCreate(
        customer_id=uuid4(),
        notes="Entrega pela manhã",
    )

    assert payload.notes == "Entrega pela manhã"


def test_order_item_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_variation_id=uuid4(),
            quantity=Decimal("0"),
        )


def test_order_item_rejects_negative_discount() -> None:
    with pytest.raises(ValidationError):
        OrderItemCreate(
            product_variation_id=uuid4(),
            quantity=Decimal("10"),
            discount_amount=Decimal("-1"),
        )