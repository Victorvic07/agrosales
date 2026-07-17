from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.modules.categories.model import Category
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.model import Product
from app.modules.products.schemas import (
    ProductCreate,
    ProductStatusUpdate,
    ProductUpdate,
)
from app.modules.products.service import (
    CategoryNotFoundError,
    InvalidProductPriceError,
    ProductAlreadyExistsError,
    ProductCodeAlreadyExistsError,
    ProductHasDependenciesError,
    ProductNotFoundError,
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

@pytest.mark.asyncio
async def test_gets_product_by_id() -> None:
    product_id = uuid4()
    expected_product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate italiano",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    product_repository.get_by_id.return_value = expected_product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )
    result = await service.get_by_id(product_id)

    assert result is expected_product
    product_repository.get_by_id.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_rejects_unknown_product_id() -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()
    product_repository.get_by_id.return_value = None

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductNotFoundError):
        await service.get_by_id(uuid4())


@pytest.mark.asyncio
async def test_updates_product_status() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate italiano",
        status=ProductStatus.ATIVO,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.update_status.return_value = product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = ProductStatusUpdate(
        status=ProductStatus.DESCONTINUADO,
    )

    result = await service.update_status(product_id, data)

    assert result is product

    product_repository.update_status.assert_awaited_once_with(
        product,
        ProductStatus.DESCONTINUADO,
    )


@pytest.mark.asyncio
async def test_deletes_product_without_variations() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate italiano",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.has_variations.return_value = False

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    await service.delete(product_id)

    product_repository.has_variations.assert_awaited_once_with(
        product_id
    )
    product_repository.delete.assert_awaited_once_with(product)


@pytest.mark.asyncio
async def test_rejects_deletion_when_product_has_variations() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate italiano",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.has_variations.return_value = True

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductHasDependenciesError):
        await service.delete(product_id)

    product_repository.delete.assert_not_awaited()

@pytest.mark.asyncio
async def test_updates_product_fields() -> None:
    product_id = uuid4()
    category_id = uuid4()

    product = Product(
        id=product_id,
        category_id=None,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
        status=ProductStatus.ATIVO,
    )

    category = Category(
        id=category_id,
        name="Hortaliças",
        is_active=True,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_name_and_category.return_value = None
    product_repository.get_by_code.return_value = None
    product_repository.update.return_value = product

    category_repository.get_by_id.return_value = category

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = ProductUpdate(
        category_id=category_id,
        code="TOM-001",
        name="Tomate italiano",
        standard_price=Decimal("18.00"),
        minimum_price=Decimal("14.00"),
        short_description="Tomate selecionado",
    )

    result = await service.update(product_id, data)

    assert result is product

    product_repository.update.assert_awaited_once_with(
        product,
        {
            "category_id": category_id,
            "code": "TOM-001",
            "name": "Tomate italiano",
            "standard_price": Decimal("18.00"),
            "minimum_price": Decimal("14.00"),
            "short_description": "Tomate selecionado",
        },
    )


@pytest.mark.asyncio
async def test_update_preserves_fields_not_informed() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        category_id=None,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
        status=ProductStatus.ATIVO,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_name_and_category.return_value = None
    product_repository.update.return_value = product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    data = ProductUpdate(name="Tomate cereja")

    await service.update(product_id, data)

    product_repository.update.assert_awaited_once_with(
        product,
        {
            "name": "Tomate cereja",
        },
    )


@pytest.mark.asyncio
async def test_update_rejects_duplicate_code_from_other_product() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )

    other_product = Product(
        id=uuid4(),
        code="TOM-001",
        name="Outro produto",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_code.return_value = other_product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductCodeAlreadyExistsError):
        await service.update(
            product_id,
            ProductUpdate(code="TOM-001"),
        )

    product_repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_allows_product_current_code() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_code.return_value = product
    product_repository.update.return_value = product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    await service.update(
        product_id,
        ProductUpdate(code="PRD-000001"),
    )

    product_repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_rejects_duplicate_name_in_category() -> None:
    product_id = uuid4()
    category_id = uuid4()

    product = Product(
        id=product_id,
        category_id=category_id,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )

    other_product = Product(
        id=uuid4(),
        category_id=category_id,
        code="PRD-000002",
        name="Tomate italiano",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_name_and_category.return_value = (
        other_product
    )

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ProductAlreadyExistsError):
        await service.update(
            product_id,
            ProductUpdate(name="Tomate italiano"),
        )


@pytest.mark.asyncio
async def test_update_rejects_invalid_final_prices() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(InvalidProductPriceError):
        await service.update(
            product_id,
            ProductUpdate(minimum_price=Decimal("20.00")),
        )

    product_repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_rejects_custom_unit_without_other_unit() -> None:
    product_id = uuid4()

    product = Product(
        id=product_id,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        custom_unit=None,
        cost_price=Decimal("8.00"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product

    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ValueError):
        await service.update(
            product_id,
            ProductUpdate(custom_unit="Saco"),
        )