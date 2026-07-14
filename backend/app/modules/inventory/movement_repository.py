from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.movement_model import InventoryMovement


class InventoryMovementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[InventoryMovement]:
        statement = select(InventoryMovement).order_by(
            InventoryMovement.created_at.desc()
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    async def list_by_lot(
        self,
        lot_id: UUID,
    ) -> list[InventoryMovement]:
        statement = (
            select(InventoryMovement)
            .where(InventoryMovement.lot_id == lot_id)
            .order_by(InventoryMovement.created_at.desc())
        )

        result = await self.session.scalars(statement)

        return list(result.all())