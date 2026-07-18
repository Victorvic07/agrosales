from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class LotStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ExpirationState(StrEnum):
    EXPIRED = "EXPIRED"
    EXPIRES_TODAY = "EXPIRES_TODAY"
    EXPIRING_SOON = "EXPIRING_SOON"
    REGULAR = "REGULAR"


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

    status: Mapped[LotStatus] = mapped_column(
        String(30),
        default=LotStatus.ACTIVE,
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

    @property
    def expiration_state(self) -> ExpirationState:
        days_until_expiration = (self.expiration_date - date.today()).days

        if days_until_expiration < 0:
            return ExpirationState.EXPIRED
        if days_until_expiration == 0:
            return ExpirationState.EXPIRES_TODAY
        if days_until_expiration <= 30:
            return ExpirationState.EXPIRING_SOON
        return ExpirationState.REGULAR
