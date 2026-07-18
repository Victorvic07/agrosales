from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

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
