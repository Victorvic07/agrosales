"""Registro central dos modelos SQLAlchemy.

A importação deste módulo garante que todas as classes mapeadas estejam
registradas antes da configuração dos relacionamentos do ORM.
"""

from app.modules.categories.model import Category
from app.modules.customers.customer_model import Customer
from app.modules.inventory.lot_model import Lot
from app.modules.inventory.movement_model import InventoryMovement
from app.modules.inventory.reservation_model import StockReservation
from app.modules.orders.order_item_model import OrderItem
from app.modules.orders.order_model import Order
from app.modules.orders.order_status_history_model import OrderStatusHistory
from app.modules.products.model import Product
from app.modules.products.variation_model import ProductVariation
from app.modules.users.model import User

__all__ = [
    "Category",
    "Customer",
    "InventoryMovement",
    "Lot",
    "Order",
    "OrderItem",
    "OrderStatusHistory",
    "Product",
    "ProductVariation",
    "StockReservation",
    "User",
]
