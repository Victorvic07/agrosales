from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.categories.model import Category
from app.modules.products.enums import ProductUnit
from app.modules.products.model import Product
from app.modules.products.schemas import ProductCreate
from app.modules.products.service import (
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    ProductCodeAlreadyExistsError,
    ProductService,
)


def make_product_data(
    *,
    category_id=None,
    code: str | None = None,
) -> ProductCreate:
    return ProductCreate(
        category_id=category_id,
        code=code,
        name="Tomate italiano",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.50"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )


@pytest.mark.asyncio
async def test_creates_product_without_category() -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_name_and_category.return_value = None
    product_repository.get_last_generated_code.return_value = None
    product_repository.exists_by_code.return_value = False

    created_product = Product(
        id=uuid4(),
        code="PRD-000001",
        name="Tomate italiano",
    )

    product_repository.create.return_value = created_product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = make_product_data()

    result = await service.create(data)

    assert result is created_product

    category_repository.get_by_id.assert_not_awaited()

    product_repository.create.assert_awaited_once_with(
        data,
        "PRD-000001",
    )


@pytest.mark.asyncio
async def test_creates_product_with_active_category() -> None:
    category_id = uuid4()

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    category_repository.get_by_id.return_value = Category(
        id=category_id,
        name="Hortaliças",
        is_active=True,
    )

    product_repository.get_by_name_and_category.return_value = None
    product_repository.get_last_generated_code.return_value = (
        "PRD-000010"
    )
    product_repository.exists_by_code.return_value = False

    product_repository.create.return_value = Product(
        id=uuid4(),
        category_id=category_id,
        code="PRD-000011",
        name="Tomate italiano",
    )

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = make_product_data(category_id=category_id)

    await service.create(data)

    category_repository.get_by_id.assert_awaited_once_with(
        category_id
    )

    product_repository.create.assert_awaited_once_with(
        data,
        "PRD-000011",
    )


@pytest.mark.asyncio
async def test_rejects_inactive_category() -> None:
    category_id = uuid4()

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    category_repository.get_by_id.return_value = Category(
        id=category_id,
        name="Hortaliças",
        is_active=False,
    )

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(CategoryNotFoundError):
        await service.create(
            make_product_data(category_id=category_id)
        )


@pytest.mark.asyncio
async def test_rejects_duplicate_name_in_same_category() -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_name_and_category.return_value = (
        Product(
            id=uuid4(),
            code="PRD-000001",
            name="Tomate italiano",
        )
    )

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductAlreadyExistsError):
        await service.create(make_product_data())


@pytest.mark.asyncio
async def test_uses_custom_product_code() -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_name_and_category.return_value = None
    product_repository.exists_by_code.return_value = False

    product_repository.create.return_value = Product(
        id=uuid4(),
        code="TOM-001",
        name="Tomate italiano",
    )

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = make_product_data(code="TOM-001")

    await service.create(data)

    product_repository.create.assert_awaited_once_with(
        data,
        "TOM-001",
    )

    product_repository.get_last_generated_code.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_duplicate_custom_code() -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_name_and_category.return_value = None
    product_repository.exists_by_code.return_value = True

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductCodeAlreadyExistsError):
        await service.create(
            make_product_data(code="TOM-001")
        )