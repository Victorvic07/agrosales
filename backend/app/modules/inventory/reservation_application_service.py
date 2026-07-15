from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.reservation_model import (
    ReservationStatus,
    StockReservation,
)
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.inventory.reservation_service import (
    FefoReservationService,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationAllocationRead,
    StockReservationRequest,
    StockReservationSummaryRead,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)


class ProductVariationNotFoundError(Exception):
    pass


class ReservationApplicationService:
    def __init__(
        self,
        session: AsyncSession,
        reservation_repository: ReservationRepository,
        variation_repository: ProductVariationRepository,
    ) -> None:
        self.session = session
        self.reservation_repository = reservation_repository
        self.variation_repository = variation_repository
        self.fefo_service = FefoReservationService()

    async def create(
        self,
        data: StockReservationRequest,
        reference_date: date | None = None,
    ) -> StockReservationSummaryRead:
        try:
            variation = await self.variation_repository.get_by_id(
                data.product_variation_id
            )

            if variation is None or not variation.is_active:
                raise ProductVariationNotFoundError(
                    "Variação de produto não encontrada ou inativa"
                )

            today = reference_date or date.today()

            lots = await self.reservation_repository.get_eligible_lots(
                product_variation_id=data.product_variation_id,
                reference_date=today,
            )

            allocations = self.fefo_service.reserve(
                lots=lots,
                requested_quantity=data.quantity,
                today=today,
            )

            lots_by_id = {
                lot.id: lot
                for lot in lots
            }

            reservations: list[
                tuple[StockReservation, object]
            ] = []

            for allocation in allocations:
                lot = lots_by_id[allocation.lot_id]

                reservation = StockReservation(
                    lot_id=lot.id,
                    quantity=allocation.quantity,
                    status=ReservationStatus.ACTIVE,
                )

                self.reservation_repository.add(reservation)

                reservations.append(
                    (
                        reservation,
                        lot,
                    )
                )

            await self.session.commit()

            for reservation, _ in reservations:
                await self.session.refresh(reservation)

            response_allocations: list[
                StockReservationAllocationRead
            ] = []

            for reservation, lot in reservations:
                response_allocations.append(
                    StockReservationAllocationRead(
                        reservation_id=reservation.id,
                        lot_id=lot.id,
                        lot_code=lot.code,
                        quantity=reservation.quantity,
                        expiration_date=lot.expiration_date,
                    )
                )

            reserved_quantity = sum(
                (
                    allocation.quantity
                    for allocation in response_allocations
                ),
                start=Decimal("0"),
            )

            return StockReservationSummaryRead(
                product_variation_id=data.product_variation_id,
                requested_quantity=data.quantity,
                reserved_quantity=reserved_quantity,
                allocations=response_allocations,
            )

        except Exception:
            await self.session.rollback()
            raise