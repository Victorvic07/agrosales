from app.modules.categories.model import Category
from app.modules.products.model import Product


def test_category_table_name() -> None:
    assert Category.__tablename__ == "categories"


def test_product_table_name() -> None:
    assert Product.__tablename__ == "products"


def test_category_defaults_to_active() -> None:
    default = Category.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True


def test_product_defaults_to_active() -> None:
    default = Product.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True