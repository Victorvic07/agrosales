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
from app.modules.orders.order_status_history_model import (
    OrderStatusHistory,
)
from app.modules.orders.order_status_history_repository import (
    OrderStatusHistoryRepository,
)


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
        history_repository: OrderStatusHistoryRepository | None = None,
    ) -> None:
        self.session = session
        self.order_repository = order_repository
        self.reservation_repository = reservation_repository
        self.history_repository = history_repository

    async def cancel(
        self,
        order_id: UUID,
        changed_by_user_id: UUID | None = None,
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

            previous_status = order.status

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

            if (
                self.history_repository is not None
                and changed_by_user_id is not None
            ):
                history = OrderStatusHistory(
                    order=order,
                    previous_status=previous_status,
                    new_status=OrderStatus.CANCELLED,
                    changed_by_user_id=changed_by_user_id,
                )

                self.history_repository.add(history)

            await self.session.commit()
            await self.session.refresh(order)

            return order

        except Exception:
            await self.session.rollback()
            raise