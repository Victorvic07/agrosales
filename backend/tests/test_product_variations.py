from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.products.variation_model import ProductVariation
from app.modules.products.variation_schemas import ProductVariationCreate


def test_product_variation_table_name() -> None:
    assert ProductVariation.__tablename__ == "product_variations"


def test_product_variation_defaults_to_active() -> None:
    default = ProductVariation.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True


def test_product_variation_accepts_valid_values() -> None:
    variation = ProductVariationCreate(
        product_id=uuid4(),
        internal_code="TOM-ITA-20-A",
        classification="Categoria A",
        package_type="Caixa 20 kg",
        unit_of_measure="CAIXA",
        weight_or_volume=Decimal("20"),
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        minimum_stock=Decimal("10"),
        commission_percentage=Decimal("3"),
    )

    assert variation.standard_price == Decimal("160")
    assert variation.commission_percentage == Decimal("3")


def test_product_variation_rejects_invalid_commission() -> None:
    with pytest.raises(ValidationError):
        ProductVariationCreate(
            product_id=uuid4(),
            internal_code="TOM-ITA-20-A",
            package_type="Caixa 20 kg",
            unit_of_measure="CAIXA",
            standard_price=Decimal("160"),
            minimum_price=Decimal("145"),
            commission_percentage=Decimal("150"),
        )