from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
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


def test_vendor_cannot_create_stock_reservation(
    client,
) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.VENDEDOR)
    )

    response = client.post(
        "/api/v1/stock-reservations",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "50",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_zero_stock_reservation_quantity(
    client,
) -> None:
    app.dependency_overrides[get_current_user] = (
        lambda: make_user(UserRole.PRODUTOR)
    )

    response = client.post(
        "/api/v1/stock-reservations",
        json={
            "product_variation_id": str(uuid4()),
            "quantity": "0",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422