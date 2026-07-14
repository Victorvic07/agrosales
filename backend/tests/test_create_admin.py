from unittest.mock import AsyncMock

import pytest

from app.scripts.create_admin import ensure_admin_exists


@pytest.mark.asyncio
async def test_admin_seed_does_not_duplicate_existing_email() -> None:
    repository = AsyncMock()
    repository.get_by_email.return_value = object()

    created = await ensure_admin_exists(
        repository=repository,
        name="Administrador",
        email="admin@agrosales.local",
        password="StrongPassword123!",
    )

    assert created is False
    repository.create.assert_not_awaited()