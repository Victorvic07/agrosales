from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot, LotStatus
from app.modules.inventory.lot_schemas import LotCreate
from app.modules.inventory.movement_model import (
    InventoryMovement,
    MovementType,
)
from app.modules.inventory.reservation_model import StockReservation


class LotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, lot_id: UUID) -> Lot | None:
        return await self.session.get(Lot, lot_id)

    async def get_by_code(self, code: str) -> Lot | None:
        statement = select(Lot).where(
            Lot.code == code.strip()
        )
        return await self.session.scalar(statement)
    
    async def get_by_code_excluding_id(
        self,
        code: str,
        lot_id: UUID,
    ) -> Lot | None:
        statement = select(Lot).where(
            Lot.code == code.strip(),
            Lot.id != lot_id,
        )

        return await self.session.scalar(statement)

    async def list_all(self) -> list[Lot]:
        statement = select(Lot).order_by(
            Lot.expiration_date,
            Lot.code,
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def create(self, data: LotCreate) -> Lot:
        lot = Lot(
            product_variation_id=data.product_variation_id,
            code=data.code.strip(),
            production_date=data.production_date,
            expiration_date=data.expiration_date,
            physical_quantity=Decimal("0"),
            reserved_quantity=Decimal("0"),
            status=LotStatus.ACTIVE,
        )

        self.session.add(lot)
        await self.session.flush()

        return lot

    async def has_blocking_history(
        self,
        lot_id: UUID,
    ) -> bool:
        reservation_statement = (
            select(func.count(StockReservation.id))
            .where(StockReservation.lot_id == lot_id)
        )

        reservation_count = await self.session.scalar(
            reservation_statement
        )

        if (reservation_count or 0) > 0:
            return True

        movement_statement = (
            select(InventoryMovement.movement_type)
            .where(InventoryMovement.lot_id == lot_id)
            .order_by(
                InventoryMovement.created_at,
                InventoryMovement.id,
            )
        )

        result = await self.session.scalars(
            movement_statement
        )
        movement_types = list(result.all())

        return movement_types not in (
            [],
            [MovementType.ENTRY],
        )