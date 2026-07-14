from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_product_repository,
    get_product_variation_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.products.model import Product
from app.modules.products.variation_model import ProductVariation
from app.modules.users.model import User


def test_admin_can_create_product_variation(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()

    product_repository = AsyncMock()
    product_repository.get_by_id.return_value = Product(
        id=product_id,
        category_id=uuid4(),
        name="Tomate",
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_internal_code.return_value = None
    variation_repository.create.return_value = ProductVariation(
        id=uuid4(),
        product_id=product_id,
        internal_code="TOM-ITA-20-A",
        classification="Categoria A",
        package_type="Caixa 20 kg",
        unit_of_measure="CAIXA",
        weight_or_volume=Decimal("20"),
        standard_price=Decimal("160"),
        minimum_price=Decimal("145"),
        minimum_stock=Decimal("10"),
        commission_percentage=Decimal("3"),
        barcode=None,
        qr_code=None,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: variation_repository
    )

    response = client.post(
        "/api/v1/product-variations",
        json={
            "product_id": str(product_id),
            "internal_code": "TOM-ITA-20-A",
            "classification": "Categoria A",
            "package_type": "Caixa 20 kg",
            "unit_of_measure": "CAIXA",
            "weight_or_volume": "20",
            "standard_price": "160",
            "minimum_price": "145",
            "minimum_stock": "10",
            "commission_percentage": "3",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["internal_code"] == "TOM-ITA-20-A"


def test_vendor_cannot_create_product_variation(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = lambda: AsyncMock()
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: AsyncMock()
    )

    response = client.post(
        "/api/v1/product-variations",
        json={
            "product_id": str(uuid4()),
            "internal_code": "TOM-ITA-20-A",
            "package_type": "Caixa 20 kg",
            "unit_of_measure": "CAIXA",
            "standard_price": "160",
            "minimum_price": "145",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_minimum_price_above_standard_price(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()

    product_repository = AsyncMock()
    product_repository.get_by_id.return_value = Product(
        id=product_id,
        category_id=uuid4(),
        name="Tomate",
        is_active=True,
    )

    variation_repository = AsyncMock()
    variation_repository.get_by_internal_code.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_product_variation_repository] = (
        lambda: variation_repository
    )

    response = client.post(
        "/api/v1/product-variations",
        json={
            "product_id": str(product_id),
            "internal_code": "TOM-ITA-20-A",
            "package_type": "Caixa 20 kg",
            "unit_of_measure": "CAIXA",
            "standard_price": "140",
            "minimum_price": "150",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "O preço mínimo não pode ser maior que o preço padrão"
    )