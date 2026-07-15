from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.reservation_model import StockReservation


class ReservationRepository:
    def __init__(self, session: AsyncSession) -> None:
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
                Lot.status.in_(("ACTIVE", "NEAR_EXPIRATION")),
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

    def add(
        self,
        reservation: StockReservation,
    ) -> None:
        self.session.add(reservation)