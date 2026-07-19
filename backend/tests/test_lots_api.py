from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.api.dependencies import (
    get_current_user,
    get_lot_repository,
    get_product_variation_repository,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.main import app
from app.modules.inventory.lot_model import Lot
from app.modules.products.variation_model import ProductVariation
from app.modules.users.model import User


def test_producer_can_create_lot(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )
    variation_id = uuid4()
    variation_repository = AsyncMock()
    variation_repository.get_by_id.return_value = ProductVariation(
        id=variation_id,
        product_id=uuid4(),
        internal_code="TOM-ITA-20-A",
        package_type="Caixa 20 kg",
        unit_of_measure="CAIXA",
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        minimum_stock=Decimal("10"),
        commission_percentage=Decimal("3"),
        is_active=True,
    )
    lot_repository = AsyncMock()
    lot_repository.get_by_code.return_value = None
    lot_repository.create.return_value = Lot(
        id=uuid4(),
        product_variation_id=variation_id,
        code="LOTE-2026-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = lambda: lot_repository
    app.dependency_overrides[get_product_variation_repository] = lambda: variation_repository
    app.dependency_overrides[get_db_session] = override_session

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(variation_id),
            "code": "LOTE-2026-001",
            "production_date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=10)).isoformat(),
            "initial_quantity": "100",
            "initial_entry_reason": "Colheita inicial",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["code"] == "LOTE-2026-001"
    session.commit.assert_awaited_once()


def test_vendor_cannot_create_lot(client) -> None:
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
    app.dependency_overrides[get_product_variation_repository] = lambda: AsyncMock()

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(uuid4()),
            "code": "LOTE-2026-001",
            "production_date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=10)).isoformat(),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_expired_lot(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = lambda: AsyncMock()
    app.dependency_overrides[get_product_variation_repository] = lambda: AsyncMock()

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(uuid4()),
            "code": "LOTE-VENCIDO",
            "production_date": (date.today() - timedelta(days=20)).isoformat(),
            "expiration_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422

def test_vendor_cannot_list_lots(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    lot_repository = AsyncMock()
    lot_repository.list_all.return_value = []

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )

    response = client.get("/api/v1/lots")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    lot_repository.list_all.assert_not_awaited()

def test_producer_can_get_lot_by_id(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    lot_id = uuid4()
    variation_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=variation_id,
        code="LOTE-2026-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
        status="ACTIVE",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()

    session = MagicMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session

    response = client.get(
        f"/api/v1/lots/{lot_id}",
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == str(lot_id)
    assert response_data["code"] == "LOTE-2026-001"
    assert response_data["available_quantity"] == "80"
    lot_repository.get_by_id.assert_awaited_once_with(lot_id)


def test_returns_404_when_lot_does_not_exist(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    lot_id = uuid4()

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()

    session = MagicMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session

    response = client.get(
        f"/api/v1/lots/{lot_id}",
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Lote não encontrado"
    lot_repository.get_by_id.assert_awaited_once_with(lot_id)

def test_producer_can_update_lot(client) -> None:
    user = User(
        id=uuid4(),
        name="Produtor",
        email="produtor@agrosales.com",
        password_hash="hash",
        role=UserRole.PRODUTOR,
        is_active=True,
    )

    lot_id = uuid4()
    variation_id = uuid4()

    lot = Lot(
        id=lot_id,
        product_variation_id=variation_id,
        code="LOTE-2026-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot
    lot_repository.has_blocking_history.return_value = False
    lot_repository.get_by_code_excluding_id.return_value = None

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    new_production_date = date.today() + timedelta(days=1)
    new_expiration_date = date.today() + timedelta(days=20)

    response = client.put(
        f"/api/v1/lots/{lot_id}",
        json={
            "code": "LOTE-2026-002",
            "production_date": new_production_date.isoformat(),
            "expiration_date": new_expiration_date.isoformat(),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["code"] == "LOTE-2026-002"
    assert response_data["production_date"] == (
        new_production_date.isoformat()
    )
    assert response_data["expiration_date"] == (
        new_expiration_date.isoformat()
    )

    lot_repository.has_blocking_history.assert_awaited_once_with(
        lot_id,
    )
    lot_repository.get_by_code_excluding_id.assert_awaited_once_with(
        "LOTE-2026-002",
        lot_id,
    )
    session.commit.assert_awaited_once()

def test_update_lot_returns_409_for_duplicate_code(client) -> None:
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
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )

    duplicate_lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-002",
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot
    lot_repository.has_blocking_history.return_value = False
    lot_repository.get_by_code_excluding_id.return_value = (
        duplicate_lot
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.put(
        f"/api/v1/lots/{lot_id}",
        json={
            "code": "LOTE-002",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Já existe um lote com esse código"
    )

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_update_lot_returns_409_when_history_blocks_edit(
    client,
) -> None:
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
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot
    lot_repository.has_blocking_history.return_value = True

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.put(
        f"/api/v1/lots/{lot_id}",
        json={
            "code": "LOTE-002",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "histórico" in response.json()["detail"]

    lot_repository.get_by_code_excluding_id.assert_not_awaited()
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()

def test_producer_can_update_lot_status(client) -> None:
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
        code="LOTE-001",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.patch(
        f"/api/v1/lots/{lot_id}/status",
        json={
            "status": "INACTIVE",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVE"

    lot_repository.get_by_id.assert_awaited_once_with(lot_id)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(lot)
    session.rollback.assert_not_awaited()


def test_status_update_returns_422_when_lot_has_reservation(
    client,
) -> None:
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
        code="LOTE-RESERVADO",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("20"),
        status="ACTIVE",
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.patch(
        f"/api/v1/lots/{lot_id}/status",
        json={"status": "INACTIVE"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "reservada" in response.json()["detail"]

    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_status_update_returns_422_for_expired_lot(
    client,
) -> None:
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
        code="LOTE-VENCIDO",
        production_date=date.today() - timedelta(days=20),
        expiration_date=date.today() - timedelta(days=1),
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="INACTIVE",
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.patch(
        f"/api/v1/lots/{lot_id}/status",
        json={"status": "ACTIVE"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "vencido" in response.json()["detail"]

    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()
    session.rollback.assert_awaited_once()


def test_status_update_returns_422_when_lot_has_no_stock(
    client,
) -> None:
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
        code="LOTE-SEM-SALDO",
        production_date=date.today(),
        expiration_date=date.today() + timedelta(days=10),
        physical_quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
        status="INACTIVE",
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_id.return_value = lot

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.patch(
        f"/api/v1/lots/{lot_id}/status",
        json={"status": "ACTIVE"},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "saldo" in response.json()["detail"]

    session.commit.assert_not_awaited()
    session.refresh.assert_not_awaited()
    session.rollback.assert_awaited_once()

@pytest.mark.parametrize(
    ("method", "path_suffix", "payload"),
    [
        ("GET", "", None),
        ("PUT", "", {"code": "LOTE-002"}),
        ("PATCH", "/status", {"status": "INACTIVE"}),
    ],
)
def test_vendor_cannot_access_individual_lot_endpoints(
    client,
    method: str,
    path_suffix: str,
    payload: dict[str, str] | None,
) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    lot_id = uuid4()
    session = MagicMock()

    async def override_session():
        yield session

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[
        get_product_variation_repository
    ] = lambda: AsyncMock()
    app.dependency_overrides[get_db_session] = override_session

    response = client.request(
        method,
        f"/api/v1/lots/{lot_id}{path_suffix}",
        json=payload,
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403
