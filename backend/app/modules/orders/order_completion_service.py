from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.reservation_model import (
    ReservationStatus,
)
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.orders.order_model import Order, OrderStatus
from app.modules.orders.order_repository import OrderRepository


class OrderNotFoundError(Exception):
    pass


class OrderCannotBeCompletedError(Exception):
    pass


class InvalidStockBalanceError(Exception):
    pass


class OrderCompletionService:
    def __init__(
        self,
        session: AsyncSession,
        order_repository: OrderRepository,
        reservation_repository: ReservationRepository,
    ) -> None:
        self.session = session
        self.order_repository = order_repository
        self.reservation_repository = reservation_repository

    async def complete(
        self,
        order_id: UUID,
    ) -> Order:
        try:
            order = await self.order_repository.get_by_id_for_update(
                order_id
            )

            if order is None:
                raise OrderNotFoundError(
                    "Pedido não encontrado"
                )

            if order.status != OrderStatus.CONFIRMED:
                raise OrderCannotBeCompletedError(
                    "Apenas pedidos confirmados podem ser concluídos"
                )

            reservations = (
                await self.reservation_repository.list_active_by_order(
                    order.id
                )
            )

            for reservation in reservations:
                lot = reservation.lot

                if (
                    lot is None
                    or lot.physical_quantity < reservation.quantity
                    or lot.reserved_quantity < reservation.quantity
                ):
                    raise InvalidStockBalanceError(
                        "Saldo de estoque do lote está inconsistente"
                    )

                lot.physical_quantity -= reservation.quantity
                lot.reserved_quantity -= reservation.quantity

                reservation.status = ReservationStatus.CONSUMED

            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(order)

            return order

        except Exception:
            await self.session.rollback()
            raise