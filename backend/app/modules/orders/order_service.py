from decimal import Decimal
from uuid import UUID

from app.core.enums import UserRole
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import Order, OrderStatus
from app.modules.orders.order_repository import (
    OrderRepository,
)
from app.modules.orders.order_schemas import (
    OrderCreate,
    OrderItemCreate,
    OrderItemUpdate,
    OrderUpdate,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)

from app.modules.orders.order_status_history_model import (
    OrderStatusHistory,
)
from app.modules.orders.order_status_history_repository import (
    OrderStatusHistoryRepository,
)


class OrderNotFoundError(Exception):
    pass


class OrderItemNotFoundError(Exception):
    pass


class OrderNotEditableError(Exception):
    pass


class InactiveCustomerError(Exception):
    pass


class ProductVariationNotFoundError(Exception):
    pass


class PriceBelowMinimumError(Exception):
    pass


class InvalidDiscountError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
        variation_repository: ProductVariationRepository,
        history_repository: OrderStatusHistoryRepository | None = None,
    ) -> None:
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.variation_repository = variation_repository
        self.history_repository = history_repository

    async def _get_editable_order(
        self,
        order_id: UUID,
    ) -> Order:
        order = await self.order_repository.get_by_id(
            order_id
        )

        if order is None:
            raise OrderNotFoundError(
                "Pedido não encontrado"
            )

        if order.status != OrderStatus.DRAFT:
            raise OrderNotEditableError(
                "Somente pedidos em rascunho podem ser alterados"
            )

        return order

    async def create_order(
        self,
        data: OrderCreate,
        seller_id: UUID,
    ) -> Order:
        customer = await self.customer_repository.get_by_id(
            data.customer_id
        )

        if customer is None or not customer.is_active:
            raise InactiveCustomerError(
                "Cliente não encontrado ou inativo"
            )

        order = Order(
            customer_id=data.customer_id,
            seller_id=seller_id,
            status=OrderStatus.DRAFT,
            subtotal=Decimal("0"),
            discount_total=Decimal("0"),
            total_amount=Decimal("0"),
            notes=data.notes,
        )

        self.order_repository.add_order(order)

        if self.history_repository is not None:
            history = OrderStatusHistory(
                order=order,
                previous_status=None,
                new_status=OrderStatus.DRAFT,
                changed_by_user_id=seller_id,
            )

            self.history_repository.add(history)

        await self.order_repository.commit()
        await self.order_repository.refresh(order)

        return order

    async def update_order(
        self,
        order_id: UUID,
        data: OrderUpdate,
    ) -> Order:
        order = await self._get_editable_order(
            order_id
        )

        if data.customer_id is not None:
            customer = await self.customer_repository.get_by_id(
                data.customer_id
            )

            if customer is None or not customer.is_active:
                raise InactiveCustomerError(
                    "Cliente não encontrado ou inativo"
                )

            order.customer_id = data.customer_id

        if "notes" in data.model_fields_set:
            order.notes = data.notes

        await self.order_repository.commit()
        await self.order_repository.refresh(order)

        return order

    def _validate_price(
        self,
        unit_price: Decimal,
        minimum_price: Decimal,
        user_role: UserRole,
    ) -> None:
        if (
            unit_price < minimum_price
            and user_role != UserRole.ADMINISTRADOR
        ):
            raise PriceBelowMinimumError(
                "Preço abaixo do mínimo permitido"
            )

    def _calculate_item_total(
        self,
        quantity: Decimal,
        unit_price: Decimal,
        discount_amount: Decimal,
    ) -> Decimal:
        gross_amount = quantity * unit_price

        if discount_amount > gross_amount:
            raise InvalidDiscountError(
                "Desconto não pode ser maior que o valor bruto"
            )

        return gross_amount - discount_amount

    def _recalculate_order(
        self,
        order: Order,
    ) -> None:
        order.subtotal = sum(
            (
                item.quantity * item.unit_price
                for item in order.items
            ),
            start=Decimal("0"),
        )

        order.discount_total = sum(
            (
                item.discount_amount
                for item in order.items
            ),
            start=Decimal("0"),
        )

        order.total_amount = (
            order.subtotal - order.discount_total
        )

    async def add_item(
        self,
        order_id: UUID,
        data: OrderItemCreate,
        user_role: UserRole,
    ) -> OrderItem:
        order = await self._get_editable_order(
            order_id
        )

        variation = await self.variation_repository.get_by_id(
            data.product_variation_id
        )

        if variation is None or not variation.is_active:
            raise ProductVariationNotFoundError(
                "Variação de produto não encontrada ou inativa"
            )

        unit_price = (
            data.unit_price
            if data.unit_price is not None
            else variation.standard_price
        )

        self._validate_price(
            unit_price=unit_price,
            minimum_price=variation.minimum_price,
            user_role=user_role,
        )

        existing_item = (
            await self.order_repository.get_item_by_variation(
                order_id=order.id,
                product_variation_id=(
                    data.product_variation_id
                ),
            )
        )

        if existing_item is not None:
            existing_item.quantity += data.quantity
            existing_item.unit_price = unit_price
            existing_item.discount_amount = (
                data.discount_amount
            )
            existing_item.total_amount = (
                self._calculate_item_total(
                    quantity=existing_item.quantity,
                    unit_price=unit_price,
                    discount_amount=data.discount_amount,
                )
            )

            item = existing_item

        else:
            item = OrderItem(
                order_id=order.id,
                product_variation_id=(
                    data.product_variation_id
                ),
                quantity=data.quantity,
                unit_price=unit_price,
                discount_amount=data.discount_amount,
                total_amount=self._calculate_item_total(
                    quantity=data.quantity,
                    unit_price=unit_price,
                    discount_amount=data.discount_amount,
                ),
            )

            self.order_repository.add_item(item)
            order.items.append(item)

        self._recalculate_order(order)

        await self.order_repository.commit()
        await self.order_repository.refresh(item)

        return item

    async def update_item(
        self,
        order_id: UUID,
        item_id: UUID,
        data: OrderItemUpdate,
        user_role: UserRole,
    ) -> OrderItem:
        order = await self._get_editable_order(
            order_id
        )

        item = await self.order_repository.get_item_by_id(
            item_id
        )

        if item is None or item.order_id != order.id:
            raise OrderItemNotFoundError(
                "Item do pedido não encontrado"
            )

        variation = await self.variation_repository.get_by_id(
            item.product_variation_id
        )

        if variation is None:
            raise ProductVariationNotFoundError(
                "Variação de produto não encontrada"
            )

        quantity = (
            data.quantity
            if data.quantity is not None
            else item.quantity
        )

        unit_price = (
            data.unit_price
            if data.unit_price is not None
            else item.unit_price
        )

        discount_amount = (
            data.discount_amount
            if data.discount_amount is not None
            else item.discount_amount
        )

        self._validate_price(
            unit_price=unit_price,
            minimum_price=variation.minimum_price,
            user_role=user_role,
        )

        item.quantity = quantity
        item.unit_price = unit_price
        item.discount_amount = discount_amount
        item.total_amount = self._calculate_item_total(
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=discount_amount,
        )

        self._recalculate_order(order)

        await self.order_repository.commit()
        await self.order_repository.refresh(item)

        return item

    async def delete_item(
        self,
        order_id: UUID,
        item_id: UUID,
    ) -> Order:
        order = await self._get_editable_order(
            order_id
        )

        item = await self.order_repository.get_item_by_id(
            item_id
        )

        if item is None or item.order_id != order.id:
            raise OrderItemNotFoundError(
                "Item do pedido não encontrado"
            )

        order.items = [
            current_item
            for current_item in order.items
            if current_item.id != item.id
        ]

        await self.order_repository.delete_item(item)

        self._recalculate_order(order)

        await self.order_repository.commit()
        await self.order_repository.refresh(order)

        return order