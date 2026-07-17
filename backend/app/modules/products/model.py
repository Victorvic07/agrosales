from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.products.enums import ProductStatus, ProductUnit


class Product(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    category_id: Mapped[UUID | None] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    unit: Mapped[ProductUnit] = mapped_column(
        Enum(
            ProductUnit,
            name="product_unit",
        ),
        default=ProductUnit.UNIDADE,
        nullable=False,
    )

    custom_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    standard_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    minimum_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    short_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    detailed_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[ProductStatus] = mapped_column(
        Enum(
            ProductStatus,
            name="product_status",
        ),
        default=ProductStatus.ATIVO,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category = relationship("Category")