from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.schemas import (
    ProductCreate,
    ProductStatusUpdate,
    ProductUpdate,
)


def valid_product_data() -> dict:
    return {
        "name": "Tomate italiano",
        "unit": ProductUnit.UNIDADE,
        "cost_price": Decimal("8.50"),
        "standard_price": Decimal("15.00"),
        "minimum_price": Decimal("12.00"),
    }


def test_create_accepts_product_without_category() -> None:
    product = ProductCreate(**valid_product_data())

    assert product.category_id is None
    assert product.code is None
    assert product.status == ProductStatus.ATIVO


def test_create_rejects_negative_cost_price() -> None:
    data = valid_product_data()
    data["cost_price"] = Decimal("-1.00")

    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_create_rejects_negative_standard_price() -> None:
    data = valid_product_data()
    data["standard_price"] = Decimal("-1.00")

    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_create_rejects_minimum_price_above_standard_price() -> None:
    data = valid_product_data()
    data["minimum_price"] = Decimal("16.00")

    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_custom_unit_is_required_for_other_unit() -> None:
    data = valid_product_data()
    data["unit"] = ProductUnit.OUTRO

    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_custom_unit_is_accepted_for_other_unit() -> None:
    data = valid_product_data()
    data["unit"] = ProductUnit.OUTRO
    data["custom_unit"] = "Saco"

    product = ProductCreate(**data)

    assert product.custom_unit == "Saco"


def test_custom_unit_is_rejected_for_fixed_unit() -> None:
    data = valid_product_data()
    data["custom_unit"] = "Saco"

    with pytest.raises(ValidationError):
        ProductCreate(**data)


def test_create_strips_text_fields() -> None:
    data = valid_product_data()
    data["name"] = "  Tomate italiano  "
    data["code"] = "  TOM-001  "
    data["short_description"] = "  Tomate selecionado  "

    product = ProductCreate(**data)

    assert product.name == "Tomate italiano"
    assert product.code == "TOM-001"
    assert product.short_description == "Tomate selecionado"


def test_update_accepts_partial_data() -> None:
    update = ProductUpdate(name="Tomate cereja")

    assert update.name == "Tomate cereja"
    assert update.standard_price is None


def test_status_update_accepts_valid_status() -> None:
    update = ProductStatusUpdate(
        status=ProductStatus.DESCONTINUADO,
    )

    assert update.status == ProductStatus.DESCONTINUADO