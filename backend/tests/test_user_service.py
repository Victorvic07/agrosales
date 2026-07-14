from unittest.mock import AsyncMock

import pytest

from app.core.enums import UserRole
from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.service import UserService


@pytest.mark.asyncio
async def test_authenticate_returns_user_for_valid_password() -> None:
    user = User(
        name="Administrador",
        email="admin@agrosales.local",
        password_hash=hash_password("StrongPassword123!"),
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    repository = AsyncMock()
    repository.get_by_email.return_value = user

    service = UserService(repository)

    authenticated = await service.authenticate(
        "admin@agrosales.local",
        "StrongPassword123!",
    )

    assert authenticated is user


@pytest.mark.asyncio
async def test_authenticate_returns_none_for_invalid_password() -> None:
    user = User(
        name="Administrador",
        email="admin@agrosales.local",
        password_hash=hash_password("StrongPassword123!"),
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    repository = AsyncMock()
    repository.get_by_email.return_value = user

    service = UserService(repository)

    authenticated = await service.authenticate(
        "admin@agrosales.local",
        "senha-errada",
    )

    assert authenticated is None