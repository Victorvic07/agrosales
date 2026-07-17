from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.modules.products.enums import ProductStatus, ProductUnit


class ProductBase(BaseModel):
    category_id: UUID | None = None

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    unit: ProductUnit = ProductUnit.UNIDADE

    custom_unit: str | None = Field(
        default=None,
        max_length=50,
    )

    cost_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    standard_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    minimum_price: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    short_description: str | None = Field(
        default=None,
        max_length=500,
    )

    detailed_description: str | None = None
    internal_notes: str | None = None

    status: ProductStatus = ProductStatus.ATIVO

    @field_validator(
        "code",
        "name",
        "custom_unit",
        "short_description",
        "detailed_description",
        "internal_notes",
        mode="before",
    )
    @classmethod
    def strip_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        stripped = value.strip()

        return stripped or None

    @model_validator(mode="after")
    def validate_prices_and_unit(
        self,
    ) -> "ProductBase":
        if self.minimum_price > self.standard_price:
            raise ValueError(
                "O preço mínimo não pode ser maior "
                "que o preço padrão"
            )

        if self.unit == ProductUnit.OUTRO:
            if not self.custom_unit:
                raise ValueError(
                    "A unidade personalizada é obrigatória "
                    "quando a unidade for OUTRO"
                )
        elif self.custom_unit is not None:
            raise ValueError(
                "A unidade personalizada só pode ser informada "
                "quando a unidade for OUTRO"
            )

        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: UUID | None = None

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    unit: ProductUnit | None = None

    custom_unit: str | None = Field(
        default=None,
        max_length=50,
    )

    cost_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    standard_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    minimum_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    short_description: str | None = Field(
        default=None,
        max_length=500,
    )

    detailed_description: str | None = None
    internal_notes: str | None = None
    status: ProductStatus | None = None

    @field_validator(
        "code",
        "name",
        "custom_unit",
        "short_description",
        "detailed_description",
        "internal_notes",
        mode="before",
    )
    @classmethod
    def strip_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        stripped = value.strip()

        return stripped or None


class ProductStatusUpdate(BaseModel):
    status: ProductStatus


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID | None

    code: str
    name: str

    unit: ProductUnit
    custom_unit: str | None

    cost_price: Decimal
    standard_price: Decimal
    minimum_price: Decimal

    short_description: str | None
    detailed_description: str | None
    internal_notes: str | None

    image_path: str | None
    status: ProductStatus