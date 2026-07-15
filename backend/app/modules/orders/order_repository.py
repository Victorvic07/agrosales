from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import Order


class OrderRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_by_id(
        self,
        order_id: UUID,
    ) -> Order | None:
        statement = (
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .where(
                Order.id == order_id
            )
        )

        return await self.session.scalar(statement)

    async def get_by_id_for_update(
        self,
        order_id: UUID,
    ) -> Order | None:
        statement = (
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .where(
                Order.id == order_id
            )
            .with_for_update()
        )

        return await self.session.scalar(statement)

    async def list_all(
        self,
    ) -> list[Order]:
        statement = (
            select(Order)
            .options(
                selectinload(Order.items)
            )
            .order_by(
                Order.created_at.desc()
            )
        )

        result = await self.session.scalars(statement)

        return list(
            result.unique().all()
        )

    def add_order(
        self,
        order: Order,
    ) -> None:
        self.session.add(order)

    async def get_item_by_id(
        self,
        item_id: UUID,
    ) -> OrderItem | None:
        return await self.session.get(
            OrderItem,
            item_id,
        )

    async def get_item_by_variation(
        self,
        order_id: UUID,
        product_variation_id: UUID,
    ) -> OrderItem | None:
        statement = select(
            OrderItem
        ).where(
            OrderItem.order_id == order_id,
            OrderItem.product_variation_id
            == product_variation_id,
        )

        return await self.session.scalar(statement)

    def add_item(
        self,
        item: OrderItem,
    ) -> None:
        self.session.add(item)

    async def delete_item(
        self,
        item: OrderItem,
    ) -> None:
        await self.session.delete(item)

    async def commit(
        self,
    ) -> None:
        await self.session.commit()

    async def refresh(
        self,
        instance: object,
    ) -> None:
        await self.session.refresh(instance)