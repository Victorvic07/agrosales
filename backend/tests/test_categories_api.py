from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_category_repository,
    get_current_user,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.categories.model import Category
from app.modules.users.model import User


def test_admin_can_create_category(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    repository = AsyncMock()
    repository.get_by_name.return_value = None

    category = Category(
        id=uuid4(),
        name="Hortaliças",
        description="Produtos hortícolas",
        is_active=True,
    )

    repository.create.return_value = category

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_category_repository] = lambda: repository

    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Hortaliças",
            "description": "Produtos hortícolas",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "Hortaliças"


def test_vendor_cannot_create_category(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    repository = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_category_repository] = lambda: repository

    response = client.post(
        "/api/v1/categories",
        json={
            "name": "Frutas",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_all_roles_can_list_categories(client) -> None:
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
        Category(
            id=uuid4(),
            name="Frutas",
            description=None,
            is_active=True,
        )
    ]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_category_repository] = lambda: repository

    response = client.get("/api/v1/categories")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Frutas"