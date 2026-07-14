from unittest.mock import AsyncMock
from uuid import uuid4

from app.core.enums import UserRole
from app.core.security import create_access_token
from app.modules.users.model import User


def test_authenticated_user_can_read_own_profile(
    client,
    mock_session: AsyncMock,
) -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    mock_session.get.return_value = user

    token = create_access_token(
        subject=str(user_id),
        role=UserRole.VENDEDOR,
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "vendedor@agrosales.com"
    assert response.json()["role"] == "VENDEDOR"


def test_vendor_cannot_access_admin_endpoint(
    client,
    mock_session: AsyncMock,
) -> None:
    user_id = uuid4()

    user = User(
        id=user_id,
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    mock_session.get.return_value = user

    token = create_access_token(
        subject=str(user_id),
        role=UserRole.VENDEDOR,
    )

    response = client.get(
        "/api/v1/users/admin-check",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Você não possui permissão para esta ação"
    )