from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.movement_model import (
    InventoryMovement,
    MovementType,
)


class InsufficientStockError(Exception):
    pass


class InventoryMovementService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register_movement(
        self,
        lot: Lot,
        user_id: UUID,
        movement_type: MovementType,
        quantity: Decimal,
        reason: str,
        notes: str | None = None,
        commit: bool = True,
    ) -> InventoryMovement:
        previous_balance = lot.physical_quantity

        if movement_type in {
            MovementType.ENTRY,
            MovementType.RETURN,
        }:
            new_balance = previous_balance + quantity

        elif movement_type in {
            MovementType.SALE,
            MovementType.LOSS,
        }:
            new_balance = previous_balance - quantity

            if new_balance < 0:
                raise InsufficientStockError(
                    "Quantidade insuficiente no lote"
                )

        elif movement_type == MovementType.ADJUSTMENT:
            new_balance = quantity

        else:
            raise ValueError(
                "Tipo de movimentação inválido"
            )

        if new_balance < lot.reserved_quantity:
            raise InsufficientStockError(
                "O saldo não pode ficar abaixo "
                "da quantidade reservada"
            )

        lot.physical_quantity = new_balance

        movement = InventoryMovement(
            lot_id=lot.id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            previous_balance=previous_balance,
            new_balance=new_balance,
            reason=reason,
            notes=notes,
        )

        self.session.add(movement)

        if commit:
            try:
                await self.session.commit()
                await self.session.refresh(movement)
            except Exception:
                await self.session.rollback()
                lot.physical_quantity = previous_balance
                raise

        return movement