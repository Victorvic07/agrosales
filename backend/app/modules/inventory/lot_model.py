from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class LotStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NEAR_EXPIRATION = "NEAR_EXPIRATION"
    EXPIRED = "EXPIRED"
    DEPLETED = "DEPLETED"


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    product_variation_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("product_variations.id"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
    )

    production_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    expiration_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    physical_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=0,
        nullable=False,
    )

    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
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

    product_variation = relationship("ProductVariation")

    @property
    def available_quantity(self) -> Decimal:
        return self.physical_quantity - self.reserved_quantity