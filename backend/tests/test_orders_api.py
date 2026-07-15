from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_customer_repository,
    get_order_repository,
    get_product_variation_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.users.model import User


def make_user(
    role: UserRole,
) -> User:
    return User(
        id=uuid4(),
        name="Usuário",
        email=f"{role.value.lower()}@agrosales.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_rejects_order_with_inactive_customer(
    client,
) -> None:
    customer_repository = AsyncMock()
    customer_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )

    app.dependency_overrides[get_customer_repository] = (
        lambda: customer_repository
    )

    app.dependency_overrides[get_order_repository] = (
        lambda: AsyncMock()
    )

    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(uuid4()),
            "notes": None,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Cliente não encontrado ou inativo"
    )


def test_rejects_zero_item_quantity(
    client,
) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.PRODUTOR)
    )

    response = client.post(
        f"/api/v1/orders/{uuid4()}/items",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "0",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422