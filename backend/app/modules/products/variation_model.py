from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ProductVariation(Base):
    __tablename__ = "product_variations"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    product_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    internal_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    classification: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    package_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    weight_or_volume: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    standard_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    minimum_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    minimum_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=0,
        nullable=False,
    )

    commission_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    barcode: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    qr_code: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    product = relationship("Product")