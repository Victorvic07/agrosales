from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CustomerType(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class DocumentType(StrEnum):
    CPF = "CPF"
    CNPJ = "CNPJ"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    customer_type: Mapped[CustomerType] = mapped_column(
        Enum(
            CustomerType,
            name="customer_type",
        ),
        nullable=False,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="customer_document_type",
        ),
        nullable=False,
    )

    document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(254),
        nullable=True,
    )

    street: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    complement: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    neighborhood: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    zip_code: Mapped[str | None] = mapped_column(
        String(8),
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