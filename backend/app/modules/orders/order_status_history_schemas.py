from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.orders.order_model import OrderStatus


class OrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    order_id: UUID
    previous_status: OrderStatus | None
    new_status: OrderStatus
    changed_by_user_id: UUID
    created_at: datetime