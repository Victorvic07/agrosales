from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import (
    Order,
    OrderStatus,
)


def test_order_table_name() -> None:
    assert Order.__tablename__ == "orders"


def test_order_item_table_name() -> None:
    assert OrderItem.__tablename__ == "order_items"


def test_order_status_values() -> None:
    assert {status.value for status in OrderStatus} == {
        "DRAFT",
        "CONFIRMED",
        "CANCELLED",
        "COMPLETED",
    }