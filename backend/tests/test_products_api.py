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
from app.modules.products.model import Product
from app.modules.users.model import User


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

    product_repository.create.return_value = Product(
        id=uuid4(),
        category_id=category_id,
        name="Tomate",
        description="Tomate italiano",
        is_active=True,
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
            "description": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "Tomate"


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
            "category_id": str(uuid4()),
            "name": "Tomate",
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
        Product(
            id=uuid4(),
            category_id=uuid4(),
            name="Tomate",
            description=None,
            is_active=True,
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