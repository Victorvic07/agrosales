from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.orders.order_model import OrderStatus


class OrderCreate(BaseModel):
    customer_id: UUID
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class OrderUpdate(BaseModel):
    customer_id: UUID | None = None
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class OrderItemCreate(BaseModel):
    product_variation_id: UUID

    quantity: Decimal = Field(
        gt=0,
    )

    unit_price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    discount_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
    )


class OrderItemUpdate(BaseModel):
    quantity: Decimal | None = Field(
        default=None,
        gt=0,
    )

    unit_price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    discount_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )


class OrderItemRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    order_id: UUID
    product_variation_id: UUID
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime


class OrderRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    customer_id: UUID
    seller_id: UUID
    status: OrderStatus
    subtotal: Decimal
    discount_total: Decimal
    total_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    completed_at: datetime | None
    items: list[OrderItemRead]