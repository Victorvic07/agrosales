from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import LotCreate
from app.modules.inventory.movement_model import MovementType
from app.modules.inventory.movement_service import InventoryMovementService
from app.modules.products.variation_repository import ProductVariationRepository


class ProductVariationNotFoundError(Exception):
    pass


class LotAlreadyExistsError(Exception):
    pass


class LotService:
    def __init__(
        self,
        session: AsyncSession,
        lot_repository: LotRepository,
        variation_repository: ProductVariationRepository,
        user_id: UUID,
    ) -> None:
        self.session = session
        self.lot_repository = lot_repository
        self.variation_repository = variation_repository
        self.user_id = user_id

    async def create(self, data: LotCreate) -> Lot:
        try:
            variation = await self.variation_repository.get_by_id(
                data.product_variation_id
            )

            if variation is None or not variation.is_active:
                raise ProductVariationNotFoundError(
                    "Variacao de produto nao encontrada ou inativa"
                )

            existing_lot = await self.lot_repository.get_by_code(data.code)

            if existing_lot is not None:
                raise LotAlreadyExistsError("Ja existe um lote com esse codigo")

            lot = await self.lot_repository.create(data)

            if data.initial_quantity > 0:
                movement_service = InventoryMovementService(self.session)
                await movement_service.register_movement(
                    lot=lot,
                    user_id=self.user_id,
                    movement_type=MovementType.ENTRY,
                    quantity=data.initial_quantity,
                    reason=data.initial_entry_reason or "",
                    notes=data.initial_entry_notes,
                    commit=False,
                )

            await self.session.commit()
            await self.session.refresh(lot)

            return lot

        except Exception:
            await self.session.rollback()
            raise
