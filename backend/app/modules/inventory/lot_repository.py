from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot, LotStatus
from app.modules.inventory.lot_schemas import LotCreate


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
