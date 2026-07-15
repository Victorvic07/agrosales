from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_customer_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.customers.customer_model import Customer
from app.modules.users.model import User


def make_user(role: UserRole) -> User:
    return User(
        id=uuid4(),
        name="Usuário",
        email=f"{role.value.lower()}@agrosales.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_vendor_cannot_inactivate_customer(client) -> None:
    customer_id = uuid4()

    repository = AsyncMock()
    repository.get_by_id.return_value = Customer(
        id=customer_id,
        customer_type="INDIVIDUAL",
        document_type="CPF",
        document="52998224725",
        name="Cliente Teste",
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.VENDEDOR
    )
    app.dependency_overrides[get_customer_repository] = (
        lambda: repository
    )

    response = client.patch(
        f"/api/v1/customers/{customer_id}/status",
        json={"is_active": False},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_invalid_customer_document(client) -> None:
    repository = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.PRODUTOR
    )
    app.dependency_overrides[get_customer_repository] = (
        lambda: repository
    )

    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "document_type": "CPF",
            "document": "111.111.111-11",
            "name": "Cliente Inválido",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == "CPF ou CNPJ inválido"