from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_category_repository,
    get_current_user,
    get_product_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.categories.model import Category
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.model import Product
from app.modules.users.model import User


def make_product(
    *,
    category_id=None,
    name: str = "Tomate",
    code: str = "PRD-000001",
    short_description: str | None = None,
) -> Product:
    return Product(
        id=uuid4(),
        category_id=category_id,
        code=code,
        name=name,
        unit=ProductUnit.UNIDADE,
        custom_unit=None,
        cost_price=Decimal("8.50"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
        short_description=short_description,
        detailed_description=None,
        internal_notes=None,
        image_path=None,
        status=ProductStatus.ATIVO,
    )


def test_admin_can_create_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    category_id = uuid4()

    category_repository = AsyncMock()
    category_repository.get_by_id.return_value = Category(
        id=category_id,
        name="Hortaliças",
        is_active=True,
    )

    product_repository = AsyncMock()
    product_repository.get_by_name_and_category.return_value = None
    product_repository.get_last_generated_code.return_value = None
    product_repository.exists_by_code.return_value = False
    product_repository.create.return_value = make_product(
        category_id=category_id,
        short_description="Tomate italiano",
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )

    response = client.post(
        "/api/v1/products",
        json={
            "category_id": str(category_id),
            "name": "Tomate",
            "unit": "UNIDADE",
            "cost_price": "8.50",
            "standard_price": "15.00",
            "minimum_price": "12.00",
            "short_description": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "Tomate"
    assert response.json()["code"] == "PRD-000001"
    assert response.json()["status"] == "ATIVO"

    product_repository.get_last_generated_code.assert_awaited_once()
    product_repository.exists_by_code.assert_awaited_once_with(
        "PRD-000001"
    )

    create_args = product_repository.create.await_args.args

    assert create_args[1] == "PRD-000001"


def test_vendor_cannot_create_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Tomate",
            "unit": "UNIDADE",
            "cost_price": "8.50",
            "standard_price": "15.00",
            "minimum_price": "12.00",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_all_roles_can_list_products(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    repository = AsyncMock()
    repository.list_all.return_value = [
        make_product(
            category_id=uuid4(),
            short_description=None,
        )
    ]

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: repository
    )

    response = client.get("/api/v1/products")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Tomate"
    assert response.json()[0]["unit"] == "UNIDADE"
    assert response.json()[0]["status"] == "ATIVO"


def test_all_roles_can_get_product_by_id(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    product_id = uuid4()
    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = make_product(
        category_id=uuid4(),
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.get(
        f"/api/v1/products/{product_id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["code"] == "PRD-000001"


def test_get_product_returns_404_when_not_found(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    product_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.get(
        f"/api/v1/products/{uuid4()}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_admin_can_update_product_status(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()

    product = make_product()
    product.status = ProductStatus.DESCONTINUADO

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.update_status.return_value = product

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.patch(
        f"/api/v1/products/{product_id}/status",
        json={
            "status": "DESCONTINUADO",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "DESCONTINUADO"


def test_vendor_cannot_update_product_status(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )

    response = client.patch(
        f"/api/v1/products/{uuid4()}/status",
        json={
            "status": "INATIVO",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_admin_can_delete_product(client) -> None:
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
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = make_product()
    product_repository.has_variations.return_value = False

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.delete(
        f"/api/v1/products/{product_id}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 204
    product_repository.delete.assert_awaited_once()


def test_delete_product_returns_conflict_when_in_use(
    client,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = make_product()
    product_repository.has_variations.return_value = True

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.delete(
        f"/api/v1/products/{uuid4()}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409


def test_vendor_cannot_delete_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )

    response = client.delete(
        f"/api/v1/products/{uuid4()}"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_admin_can_update_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()
    category_id = uuid4()

    product = make_product(
        category_id=category_id,
        name="Tomate italiano",
        code="TOM-001",
        short_description="Tomate selecionado",
    )
    product.standard_price = Decimal("18.00")
    product.minimum_price = Decimal("14.00")

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_name_and_category.return_value = None
    product_repository.get_by_code.return_value = None
    product_repository.update.return_value = product

    category_repository.get_by_id.return_value = Category(
        id=category_id,
        name="Hortaliças",
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": str(category_id),
            "code": "TOM-001",
            "name": "Tomate italiano",
            "standard_price": "18.00",
            "minimum_price": "14.00",
            "short_description": "Tomate selecionado",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["code"] == "TOM-001"
    assert response.json()["name"] == "Tomate italiano"
    assert response.json()["standard_price"] == "18.00"


def test_update_product_returns_404_when_not_found(
    client,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    product_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.put(
        f"/api/v1/products/{uuid4()}",
        json={
            "name": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_update_product_returns_conflict_for_duplicate_code(
    client,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()

    product = make_product()
    other_product = make_product(
        code="TOM-001",
        name="Outro produto",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_code.return_value = other_product

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "code": "TOM-001",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409


def test_update_product_returns_conflict_for_duplicate_name(
    client,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product_id = uuid4()
    category_id = uuid4()

    product = make_product(
        category_id=category_id,
    )

    other_product = make_product(
        category_id=category_id,
        code="PRD-000002",
        name="Tomate italiano",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product
    product_repository.get_by_name_and_category.return_value = (
        other_product
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409


def test_update_product_returns_422_for_invalid_final_prices(
    client,
) -> None:
    user = User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )

    product = make_product()
    product.standard_price = Decimal("15.00")
    product.minimum_price = Decimal("12.00")

    product_repository = AsyncMock()
    category_repository = AsyncMock()

    product_repository.get_by_id.return_value = product

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )

    response = client.put(
        f"/api/v1/products/{uuid4()}",
        json={
            "minimum_price": "20.00",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_vendor_cannot_update_product(client) -> None:
    user = User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )

    response = client.put(
        f"/api/v1/products/{uuid4()}",
        json={
            "name": "Tomate italiano",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403