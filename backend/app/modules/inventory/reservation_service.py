from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.modules.inventory.lot_model import Lot, LotStatus


class InsufficientAvailableStockError(Exception):
    pass


@dataclass(frozen=True)
class LotAllocation:
    lot_id: UUID
    quantity: Decimal


class FefoReservationService:
    def reserve(
        self,
        lots: list[Lot],
        requested_quantity: Decimal,
        today: date | None = None,
    ) -> list[LotAllocation]:
        if requested_quantity <= 0:
            raise ValueError(
                "A quantidade solicitada deve ser maior que zero"
            )

        reference_date = today or date.today()

        eligible_lots = sorted(
            (
                lot
                for lot in lots
                if lot.expiration_date >= reference_date
                and lot.status == LotStatus.ACTIVE
                and lot.available_quantity > 0
            ),
            key=lambda lot: (
                lot.expiration_date,
                lot.production_date,
                lot.code,
            ),
        )

        remaining_quantity = requested_quantity
        allocations: list[LotAllocation] = []

        for lot in eligible_lots:
            if remaining_quantity <= 0:
                break

            allocated_quantity = min(
                lot.available_quantity,
                remaining_quantity,
            )

            allocations.append(
                LotAllocation(
                    lot_id=lot.id,
                    quantity=allocated_quantity,
                )
            )

            remaining_quantity -= allocated_quantity

        if remaining_quantity > 0:
            raise InsufficientAvailableStockError(
                "Estoque disponível insuficiente para realizar a reserva"
            )

        allocations_by_lot = {
            allocation.lot_id: allocation.quantity
            for allocation in allocations
        }

        for lot in eligible_lots:
            allocated_quantity = allocations_by_lot.get(lot.id)

            if allocated_quantity is not None:
                lot.reserved_quantity += allocated_quantity

        return allocations
