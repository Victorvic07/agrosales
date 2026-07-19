from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.movement_model import InventoryMovement


class InventoryMovementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        movement_id: UUID,
    ) -> InventoryMovement | None:
        statement = (
            select(InventoryMovement)
            .options(
                selectinload(
                    InventoryMovement.user,
                ),
            )
            .where(
                InventoryMovement.id == movement_id,
            )
        )

        return await self.session.scalar(statement)

    async def list_all(
        self,
    ) -> list[InventoryMovement]:
        statement = (
            select(InventoryMovement)
            .options(
                selectinload(
                    InventoryMovement.user,
                ),
            )
            .order_by(
                InventoryMovement.created_at.desc(),
            )
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    async def list_by_lot(
        self,
        lot_id: UUID,
    ) -> list[InventoryMovement]:
        statement = (
            select(InventoryMovement)
            .options(
                selectinload(
                    InventoryMovement.user,
                ),
            )
            .where(
                InventoryMovement.lot_id == lot_id,
            )
            .order_by(
                InventoryMovement.created_at.desc(),
            )
        )

        result = await self.session.scalars(statement)

        return list(result.all())