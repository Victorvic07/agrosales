from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.customer_repository import (
    CustomerRepository,
)
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


class OrderCannotBeConfirmedError(Exception):
    pass


class OrderWithoutItemsError(Exception):
    pass


class InactiveCustomerError(Exception):
    pass


class OrderConfirmationService:
    def __init__(
        self,
        session: AsyncSession,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
        reservation_repository: ReservationRepository,
        history_repository: OrderStatusHistoryRepository | None = None,
    ) -> None:
        self.session = session
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.reservation_repository = reservation_repository
        self.history_repository = history_repository
        self.fefo_service = FefoReservationService()

    async def confirm(
        self,
        order_id: UUID,
        changed_by_user_id: UUID | None = None,
        reference_date: date | None = None,
    ) -> Order:
        try:
            order = await self.order_repository.get_by_id_for_update(
                order_id
            )

            if order is None:
                raise OrderNotFoundError(
                    "Pedido não encontrado"
                )

            if order.status != OrderStatus.DRAFT:
                raise OrderCannotBeConfirmedError(
                    "Somente pedidos em rascunho podem ser confirmados"
                )

            if not order.items:
                raise OrderWithoutItemsError(
                    "O pedido precisa ter ao menos um item"
                )

            customer = await self.customer_repository.get_by_id(
                order.customer_id
            )

            if customer is None or not customer.is_active:
                raise InactiveCustomerError(
                    "Cliente não encontrado ou inativo"
                )

            today = reference_date or date.today()

            for item in order.items:
                lots = (
                    await self.reservation_repository.get_eligible_lots(
                        product_variation_id=(
                            item.product_variation_id
                        ),
                        reference_date=today,
                    )
                )

                allocations = self.fefo_service.reserve(
                    lots=lots,
                    requested_quantity=item.quantity,
                    today=today,
                )

                for allocation in allocations:
                    reservation = StockReservation(
                        lot_id=allocation.lot_id,
                        order_item_id=item.id,
                        quantity=allocation.quantity,
                        status=ReservationStatus.ACTIVE,
                    )

                    self.reservation_repository.add(
                        reservation
                    )

            previous_status = order.status

            order.status = OrderStatus.CONFIRMED
            order.confirmed_at = datetime.now(timezone.utc)

            if (
                self.history_repository is not None
                and changed_by_user_id is not None
            ):
                history = OrderStatusHistory(
                    order=order,
                    previous_status=previous_status,
                    new_status=OrderStatus.CONFIRMED,
                    changed_by_user_id=changed_by_user_id,
                )

                self.history_repository.add(history)

            await self.session.commit()
            await self.session.refresh(order)

            return order

        except Exception:
            await self.session.rollback()
            raise