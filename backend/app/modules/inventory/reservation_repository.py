from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.lot_model import Lot, LotStatus
from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.orders.order_item_model import OrderItem


class ReservationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_eligible_lots(
        self,
        product_variation_id: UUID,
        reference_date: date,
    ) -> list[Lot]:
        statement = (
            select(Lot)
            .where(
                Lot.product_variation_id == product_variation_id,
                Lot.expiration_date >= reference_date,
                Lot.status == LotStatus.ACTIVE,
                Lot.physical_quantity > Lot.reserved_quantity,
            )
            .order_by(
                Lot.expiration_date.asc(),
                Lot.production_date.asc(),
                Lot.code.asc(),
            )
            .with_for_update()
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    async def list_active_by_order(
        self,
        order_id: UUID,
    ) -> list[StockReservation]:
        statement = (
            select(StockReservation)
            .join(
                OrderItem,
                StockReservation.order_item_id == OrderItem.id,
            )
            .options(
                selectinload(StockReservation.lot)
            )
            .where(
                OrderItem.order_id == order_id,
                StockReservation.status == ReservationStatus.ACTIVE,
            )
            .with_for_update()
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    def add(
        self,
        reservation: StockReservation,
    ) -> None:
        self.session.add(reservation)
