from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_category_repository,
    get_current_user,
    get_product_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.categories.model import Category
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.model import Product
from app.modules.users.model import User


def make_product(
    *,
    category_id=None,
    name: str = "Tomate",
    code: str = "PRD-000001",
    short_description: str | None = None,
) -> Product:
    return Product(
        id=uuid4(),
        category_id=category_id,
        code=code,
        name=name,
        unit=ProductUnit.UNIDADE,
        custom_unit=None,
        cost_price=Decimal("8.50"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
        short_description=short_description,
        detailed_description=None,
        internal_notes=None,
        image_path=None,
        status=ProductStatus.ATIVO,
    )


def test_admin_can_create_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    category_id = uuid4()

    category_repository = AsyncMock()
    category_repository.get_by_id.return_value = Category(
        id=category_id,
        name="Hortaliças",
        is_active=True,
    )

    product_repository = AsyncMock()
    product_repository.get_by_name_and_category.return_value = None
    product_repository.create.return_value = make_product(
        category_id=category_id,
        short_description="Tomate italiano",
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )

    response = client.post(
        "/api/v1/products",
        json={
            "category_id": str(category_id),
            "name": "Tomate",
            "unit": "UNIDADE",
            "cost_price": "8.50",
            "standard_price": "15.00",
            "minimum_price": "12.00",
            "short_description": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "Tomate"
    assert response.json()["code"] == "PRD-000001"
    assert response.json()["status"] == "ATIVO"


def test_vendor_cannot_create_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Tomate",
            "unit": "UNIDADE",
            "cost_price": "8.50",
            "standard_price": "15.00",
            "minimum_price": "12.00",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_all_roles_can_list_products(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    repository = AsyncMock()
    repository.list_all.return_value = [
        make_product(
            category_id=uuid4(),
            short_description=None,
        )
    ]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: repository
    )

    response = client.get("/api/v1/products")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Tomate"
    assert response.json()[0]["unit"] == "UNIDADE"
    assert response.json()[0]["status"] == "ATIVO"