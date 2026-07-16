from uuid import uuid4

from app.modules.orders.order_model import OrderStatus
from app.modules.orders.order_status_history_model import (
    OrderStatusHistory,
)


def test_creates_order_status_history_record() -> None:
    order_id = uuid4()
    user_id = uuid4()

    history = OrderStatusHistory(
        order_id=order_id,
        previous_status=None,
        new_status=OrderStatus.DRAFT,
        changed_by_user_id=user_id,
    )

    assert history.order_id == order_id
    assert history.previous_status is None
    assert history.new_status == OrderStatus.DRAFT
    assert history.changed_by_user_id == user_id