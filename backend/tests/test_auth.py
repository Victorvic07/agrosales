from unittest.mock import AsyncMock
from uuid import uuid4

from app.core.enums import UserRole
from app.core.security import hash_password
from app.modules.users.model import User


def test_login_returns_bearer_token(
    client,
    mock_session: AsyncMock,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.local",
        password_hash=hash_password("StrongPassword123!"),
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    mock_session.scalar.return_value = user

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@agrosales.local",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert isinstance(response.json()["access_token"], str)


def test_login_rejects_invalid_credentials(
    client,
    mock_session: AsyncMock,
) -> None:
    mock_session.scalar.return_value = None

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "missing@agrosales.local",
            "password": "senha-errada",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos"