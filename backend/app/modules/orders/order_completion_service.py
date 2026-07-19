from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.movement_model import MovementType
from app.modules.inventory.movement_service import InventoryMovementService
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
        history_repository: OrderStatusHistoryRepository | None = None,
        movement_service: InventoryMovementService | None = None,
    ) -> None:
        self.session = session
        self.order_repository = order_repository
        self.reservation_repository = reservation_repository
        self.history_repository = history_repository
        self.movement_service = (
            movement_service
            or InventoryMovementService(session)
        )

    async def complete(
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

                lot.reserved_quantity -= reservation.quantity

                await self.movement_service.register_movement(
                    lot=lot,
                    user_id=(
                        changed_by_user_id
                        or order.seller_id
                    ),
                    movement_type=MovementType.SALE,
                    quantity=reservation.quantity,
                    reason=f"Baixa do pedido {order.id}",
                    notes=None,
                    commit=False,
                )

                reservation.status = ReservationStatus.CONSUMED

            previous_status = order.status

            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.now(UTC)

            if (
                self.history_repository is not None
                and changed_by_user_id is not None
            ):
                history = OrderStatusHistory(
                    order=order,
                    previous_status=previous_status,
                    new_status=OrderStatus.COMPLETED,
                    changed_by_user_id=changed_by_user_id,
                )

                self.history_repository.add(history)

            await self.session.commit()
            await self.session.refresh(order)

            return order

        except Exception:
            await self.session.rollback()
            raise