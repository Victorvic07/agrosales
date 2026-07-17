from decimal import Decimal

from app.modules.categories.model import Category
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.model import Product


def test_category_table_name() -> None:
    assert Category.__tablename__ == "categories"


def test_product_table_name() -> None:
    assert Product.__tablename__ == "products"


def test_category_defaults_to_active() -> None:
    default = Category.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True


def test_product_defaults_to_active_status() -> None:
    default = Product.__table__.c.status.default

    assert default is not None
    assert default.arg == ProductStatus.ATIVO


def test_product_defaults_to_unit() -> None:
    default = Product.__table__.c.unit.default

    assert default is not None
    assert default.arg == ProductUnit.UNIDADE


def test_product_category_is_optional() -> None:
    assert Product.__table__.c.category_id.nullable is True


def test_product_code_is_unique() -> None:
    assert Product.__table__.c.code.unique is True


def test_product_price_precision() -> None:
    assert Product.__table__.c.cost_price.type.precision == 12
    assert Product.__table__.c.cost_price.type.scale == 2

    assert Product.__table__.c.standard_price.type.precision == 12
    assert Product.__table__.c.standard_price.type.scale == 2

    assert Product.__table__.c.minimum_price.type.precision == 12
    assert Product.__table__.c.minimum_price.type.scale == 2


def test_product_price_defaults() -> None:
    product = Product(
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("0.00"),
        standard_price=Decimal("0.00"),
        minimum_price=Decimal("0.00"),
    )

    assert product.status in (None, ProductStatus.ATIVO)