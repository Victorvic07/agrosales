from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.orders.order_status_history_model import (
    OrderStatusHistory,
)


class OrderStatusHistoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    def add(
        self,
        history: OrderStatusHistory,
    ) -> None:
        self.session.add(history)

    async def list_by_order(
        self,
        order_id: UUID,
    ) -> list[OrderStatusHistory]:
        statement = (
            select(OrderStatusHistory)
            .where(
                OrderStatusHistory.order_id == order_id
            )
            .order_by(
                OrderStatusHistory.created_at.asc()
            )
        )

        result = await self.session.scalars(statement)

        return list(result.all())