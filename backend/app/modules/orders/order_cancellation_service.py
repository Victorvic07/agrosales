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


class OrderCannotBeCancelledError(Exception):
    pass


class InvalidReservedStockError(Exception):
    pass


class OrderCancellationService:
    def __init__(
        self,
        session: AsyncSession,
        order_repository: OrderRepository,
        reservation_repository: ReservationRepository,
    ) -> None:
        self.session = session
        self.order_repository = order_repository
        self.reservation_repository = reservation_repository

    async def cancel(
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

            if order.status == OrderStatus.COMPLETED:
                raise OrderCannotBeCancelledError(
                    "Pedido concluído não pode ser cancelado"
                )

            if order.status == OrderStatus.CANCELLED:
                raise OrderCannotBeCancelledError(
                    "Pedido já está cancelado"
                )

            if order.status == OrderStatus.CONFIRMED:
                reservations = (
                    await self.reservation_repository.list_active_by_order(
                        order.id
                    )
                )

                for reservation in reservations:
                    lot = reservation.lot

                    if lot is None:
                        raise InvalidReservedStockError(
                            "Lote da reserva não encontrado"
                        )

                    if (
                        lot.reserved_quantity
                        < reservation.quantity
                    ):
                        raise InvalidReservedStockError(
                            "Saldo reservado do lote está inconsistente"
                        )

                    lot.reserved_quantity -= reservation.quantity
                    reservation.status = ReservationStatus.RELEASED

            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(order)

            return order

        except Exception:
            await self.session.rollback()
            raise