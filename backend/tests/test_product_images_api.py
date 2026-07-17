from decimal import Decimal
from io import BytesIO
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from PIL import Image

from app.api.dependencies import (
    get_category_repository,
    get_current_user,
    get_product_image_service,
    get_product_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.model import Product
from app.modules.users.model import User


def create_image_bytes() -> bytes:
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (400, 300),
        "white",
    )

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


def make_product(
    *,
    image_path: str | None = None,
) -> Product:
    return Product(
        id=uuid4(),
        category_id=None,
        code="PRD-000001",
        name="Tomate",
        unit=ProductUnit.UNIDADE,
        custom_unit=None,
        cost_price=Decimal("8.50"),
        standard_price=Decimal("15.00"),
        minimum_price=Decimal("12.00"),
        short_description=None,
        detailed_description=None,
        internal_notes=None,
        image_path=image_path,
        status=ProductStatus.ATIVO,
    )


def make_admin() -> User:
    return User(
        id=uuid4(),
        name="Administrador",
        email="admin@agrosales.com",
        password_hash="hash",
        role=UserRole.ADMINISTRADOR,
        is_active=True,
    )


def make_vendor() -> User:
    return User(
        id=uuid4(),
        name="Vendedor",
        email="vendedor@agrosales.com",
        password_hash="hash",
        role=UserRole.VENDEDOR,
        is_active=True,
    )


def test_admin_can_upload_product_image(client) -> None:
    product_id = uuid4()
    product = make_product(
        image_path="products/PRD-000001-imagem.webp",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    image_service = Mock()

    product_repository.get_by_id.return_value = product
    image_service.save.return_value = (
        "products/PRD-000001-imagem.webp"
    )
    product_repository.update_image_path.return_value = product

    app.dependency_overrides[get_current_user] = make_admin
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_image_service] = (
        lambda: image_service
    )

    response = client.post(
        f"/api/v1/products/{product_id}/image",
        files={
            "file": (
                "tomate.png",
                create_image_bytes(),
                "image/png",
            )
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["image_path"] == (
        "products/PRD-000001-imagem.webp"
    )

    image_service.save.assert_called_once()

    product_repository.update_image_path.assert_awaited_once_with(
        product,
        "products/PRD-000001-imagem.webp",
    )


def test_upload_returns_404_for_unknown_product(client) -> None:
    product_repository = AsyncMock()
    category_repository = AsyncMock()
    image_service = Mock()

    product_repository.get_by_id.return_value = None

    app.dependency_overrides[get_current_user] = make_admin
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_image_service] = (
        lambda: image_service
    )

    response = client.post(
        f"/api/v1/products/{uuid4()}/image",
        files={
            "file": (
                "tomate.png",
                create_image_bytes(),
                "image/png",
            )
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 404


def test_upload_rejects_invalid_image(client) -> None:
    product = make_product()

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    image_service = Mock()

    product_repository.get_by_id.return_value = product
    image_service.save.side_effect = ValueError(
        "Imagem inválida"
    )

    app.dependency_overrides[get_current_user] = make_admin
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_image_service] = (
        lambda: image_service
    )

    response = client.post(
        f"/api/v1/products/{uuid4()}/image",
        files={
            "file": (
                "arquivo.pdf",
                b"arquivo-invalido",
                "application/pdf",
            )
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_admin_can_remove_product_image(client) -> None:
    product = make_product(
        image_path="products/imagem.webp",
    )

    product_repository = AsyncMock()
    category_repository = AsyncMock()
    image_service = Mock()

    product_repository.get_by_id.return_value = product
    product_repository.update_image_path.return_value = product

    app.dependency_overrides[get_current_user] = make_admin
    app.dependency_overrides[get_product_repository] = (
        lambda: product_repository
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: category_repository
    )
    app.dependency_overrides[get_product_image_service] = (
        lambda: image_service
    )

    response = client.delete(
        f"/api/v1/products/{uuid4()}/image"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200

    image_service.remove.assert_called_once_with(
        "products/imagem.webp"
    )

    product_repository.update_image_path.assert_awaited_once_with(
        product,
        None,
    )


def test_vendor_cannot_upload_product_image(client) -> None:
    app.dependency_overrides[get_current_user] = make_vendor
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_product_image_service] = Mock

    response = client.post(
        f"/api/v1/products/{uuid4()}/image",
        files={
            "file": (
                "tomate.png",
                create_image_bytes(),
                "image/png",
            )
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_vendor_cannot_remove_product_image(client) -> None:
    app.dependency_overrides[get_current_user] = make_vendor
    app.dependency_overrides[get_product_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_category_repository] = (
        lambda: AsyncMock()
    )
    app.dependency_overrides[get_product_image_service] = Mock

    response = client.delete(
        f"/api/v1/products/{uuid4()}/image"
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403