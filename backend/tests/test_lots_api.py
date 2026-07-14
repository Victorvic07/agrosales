from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_lot_repository,
    get_product_variation_repository,
)
from app.core.enums import UserRole
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
        physical_quantity=Decimal("100"),
        reserved_quantity=Decimal("0"),
        status="ACTIVE",
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: variation_repository
    )

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(variation_id),
            "code": "LOTE-2026-001",
            "production_date": date.today().isoformat(),
            "expiration_date": (
                date.today() + timedelta(days=10)
            ).isoformat(),
            "physical_quantity": "100",
            "reserved_quantity": "0",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["code"] == "LOTE-2026-001"


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
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: AsyncMock()
    )

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(uuid4()),
            "code": "LOTE-2026-001",
            "production_date": date.today().isoformat(),
            "expiration_date": (
                date.today() + timedelta(days=10)
            ).isoformat(),
            "physical_quantity": "100",
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
        is_active=True,
    )

    lot_repository = AsyncMock()
    lot_repository.get_by_code.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_lot_repository] = (
        lambda: lot_repository
    )
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: variation_repository
    )

    response = client.post(
        "/api/v1/lots",
        json={
            "product_variation_id": str(variation_id),
            "code": "LOTE-VENCIDO",
            "production_date": (
                date.today() - timedelta(days=20)
            ).isoformat(),
            "expiration_date": (
                date.today() - timedelta(days=1)
            ).isoformat(),
            "physical_quantity": "50",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Não é permitido cadastrar um lote já vencido"
    )