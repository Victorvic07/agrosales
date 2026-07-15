import re
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.modules.customers.customer_model import (
    CustomerType,
    DocumentType,
)


def digits_only(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    return re.sub(r"\D", "", value)


class CustomerBase(BaseModel):
    customer_type: CustomerType
    document_type: DocumentType

    document: str = Field(
        min_length=11,
        max_length=18,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    street: str | None = Field(
        default=None,
        max_length=150,
    )

    number: str | None = Field(
        default=None,
        max_length=20,
    )

    complement: str | None = Field(
        default=None,
        max_length=100,
    )

    neighborhood: str | None = Field(
        default=None,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )

    zip_code: str | None = Field(
        default=None,
        max_length=9,
    )

    @field_validator(
        "document",
        "phone",
        "zip_code",
        mode="before",
    )
    @classmethod
    def normalize_numeric_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return digits_only(value)

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Nome do cliente é obrigatório"
            )

        return normalized

    @field_validator("state")
    @classmethod
    def normalize_state(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_type: CustomerType | None = None
    document_type: DocumentType | None = None

    document: str | None = Field(
        default=None,
        min_length=11,
        max_length=18,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    street: str | None = Field(
        default=None,
        max_length=150,
    )

    number: str | None = Field(
        default=None,
        max_length=20,
    )

    complement: str | None = Field(
        default=None,
        max_length=100,
    )

    neighborhood: str | None = Field(
        default=None,
        max_length=100,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )

    zip_code: str | None = Field(
        default=None,
        max_length=9,
    )

    @field_validator(
        "document",
        "phone",
        "zip_code",
        mode="before",
    )
    @classmethod
    def normalize_numeric_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return digits_only(value)

    @field_validator("name")
    @classmethod
    def normalize_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Nome do cliente é obrigatório"
            )

        return normalized

    @field_validator("state")
    @classmethod
    def normalize_state(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class CustomerStatusUpdate(BaseModel):
    is_active: bool


class CustomerRead(CustomerBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime