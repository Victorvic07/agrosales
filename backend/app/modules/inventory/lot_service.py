from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot, LotStatus
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import LotCreate, LotUpdate
from app.modules.inventory.movement_model import MovementType
from app.modules.inventory.movement_service import InventoryMovementService
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)


class ProductVariationNotFoundError(Exception):
    pass


class LotAlreadyExistsError(Exception):
    pass


class LotNotFoundError(Exception):
    pass


class LotEditBlockedError(Exception):
    pass

class LotStatusChangeBlockedError(Exception):
    pass


class LotService:
    def __init__(
        self,
        session: AsyncSession,
        lot_repository: LotRepository,
        variation_repository: ProductVariationRepository,
        user_id: UUID,
        movement_service: InventoryMovementService | None = None,
    ) -> None:
        self.session = session
        self.lot_repository = lot_repository
        self.variation_repository = variation_repository
        self.user_id = user_id
        self.movement_service = (
            movement_service
            or InventoryMovementService(session)
        )

    async def get(self, lot_id: UUID) -> Lot:
        lot = await self.lot_repository.get_by_id(lot_id)

        if lot is None:
            raise LotNotFoundError("Lote não encontrado")

        return lot
    
    async def change_status(
        self,
        lot_id: UUID,
        new_status: LotStatus,
    ) -> Lot:
        lot = await self.get(lot_id)
        previous_status = lot.status

        try:
            if new_status == LotStatus.INACTIVE:
                if lot.reserved_quantity > 0:
                    raise LotStatusChangeBlockedError(
                        "O lote não pode ser inativado porque "
                        "possui quantidade reservada"
                    )

            elif new_status == LotStatus.ACTIVE:
                if lot.expiration_date < date.today():
                    raise LotStatusChangeBlockedError(
                        "O lote vencido não pode ser reativado"
                    )

                if lot.physical_quantity <= 0:
                    raise LotStatusChangeBlockedError(
                        "O lote sem saldo não pode ser reativado"
                    )

            lot.status = new_status

            await self.session.commit()
            await self.session.refresh(lot)

            return lot

        except Exception:
            await self.session.rollback()
            lot.status = previous_status
            raise

    async def update(
        self,
        lot_id: UUID,
        data: LotUpdate,
    ) -> Lot:
        try:
            lot = await self.get(lot_id)

            has_blocking_history = (
                await self.lot_repository.has_blocking_history(
                    lot_id
                )
            )

            if has_blocking_history:
                raise LotEditBlockedError(
                    "O lote não pode ser editado porque "
                    "possui histórico de movimentações ou reservas"
                )

            if data.code is not None:
                normalized_code = data.code.strip()

                existing_lot = (
                    await self.lot_repository.get_by_code_excluding_id(
                        normalized_code,
                        lot_id,
                    )
                )

                if existing_lot is not None:
                    raise LotAlreadyExistsError(
                        "Já existe um lote com esse código"
                    )

                lot.code = normalized_code

            if data.production_date is not None:
                lot.production_date = data.production_date

            if data.expiration_date is not None:
                lot.expiration_date = data.expiration_date

            await self.session.commit()
            await self.session.refresh(lot)

            return lot

        except Exception:
            await self.session.rollback()
            raise

        

    async def create(self, data: LotCreate) -> Lot:
        try:
            variation = (
                await self.variation_repository.get_by_id(
                    data.product_variation_id
                )
            )

            if variation is None or not variation.is_active:
                raise ProductVariationNotFoundError(
                    "Variacao de produto nao encontrada ou inativa"
                )

            existing_lot = await self.lot_repository.get_by_code(
                data.code
            )

            if existing_lot is not None:
                raise LotAlreadyExistsError(
                    "Ja existe um lote com esse codigo"
                )

            lot = await self.lot_repository.create(data)

            if data.initial_quantity > 0:
                await self.movement_service.register_movement(
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