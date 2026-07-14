from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_lot_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
from app.modules.inventory.lot_model import Lot
from app.modules.users.model import User


def test_producer_can_register_inventory_entry(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    lot_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=uuid4(),
        code="LOTE-2026-001",
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    session = MagicMock()
    session.commit = AsyncMock()

    async def refresh_movement(movement) -> None:
        movement.id = uuid4()

    session.refresh = AsyncMock(side_effect=refresh_movement)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session

    response = client.post(
        "/api/v1/inventory-movements",
        json={
            "lot_id": str(lot_id),
            "movement_type": "ENTRY",
            "quantity": "50",
            "reason": "Entrada de produção",
            "notes": None,
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["previous_balance"] == "100"
    assert response.json()["new_balance"] == "150"


def test_vendor_cannot_register_inventory_movement(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = lambda: AsyncMock()

    response = client.post(
        "/api/v1/inventory-movements",
        json={
            "lot_id": str(uuid4()),
            "movement_type": "ENTRY",
            "quantity": "50",
            "reason": "Entrada de produção",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_movement_when_lot_does_not_exist(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )

    response = client.post(
        "/api/v1/inventory-movements",
        json={
            "lot_id": str(uuid4()),
            "movement_type": "LOSS",
            "quantity": "10",
            "reason": "Produto avariado",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Lote não encontrado"