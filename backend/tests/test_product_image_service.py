from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from app.modules.products.image_service import (
    InvalidProductImageError,
    ProductImageService,
    ProductImageTooLargeError,
)


def create_image_bytes(
    *,
    width: int = 400,
    height: int = 300,
    image_format: str = "PNG",
) -> bytes:
    buffer = BytesIO()

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    image.save(
        buffer,
        format=image_format,
    )

    return buffer.getvalue()


def test_saves_image_as_webp(
    tmp_path: Path,
) -> None:
    service = ProductImageService(
        upload_directory=tmp_path,
    )

    relative_path = service.save(
        product_code="PRD-000001",
        content=create_image_bytes(),
        content_type="image/png",
    )

    saved_path = tmp_path / relative_path

    assert saved_path.exists()
    assert saved_path.suffix == ".webp"
    assert saved_path.parent.name == "products"
    assert saved_path.name.startswith("PRD-000001-")


def test_resizes_image_to_maximum_dimension(
    tmp_path: Path,
) -> None:
    service = ProductImageService(
        upload_directory=tmp_path,
    )

    relative_path = service.save(
        product_code="PRD-000001",
        content=create_image_bytes(
            width=2400,
            height=1800,
        ),
        content_type="image/png",
    )

    saved_path = tmp_path / relative_path

    with Image.open(saved_path) as image:
        assert image.width <= 1200
        assert image.height <= 1200
        assert image.width == 1200
        assert image.height == 900


def test_rejects_unsupported_content_type(
    tmp_path: Path,
) -> None:
    service = ProductImageService(
        upload_directory=tmp_path,
    )

    with pytest.raises(InvalidProductImageError):
        service.save(
            product_code="PRD-000001",
            content=b"arquivo",
            content_type="application/pdf",
        )


def test_rejects_image_larger_than_five_megabytes(
    tmp_path: Path,
) -> None:
    service = ProductImageService(
        upload_directory=tmp_path,
    )

    with pytest.raises(ProductImageTooLargeError):
        service.save(
            product_code="PRD-000001",
            content=b"x" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )


def test_replaces_previous_product_image(
    tmp_path: Path,
) -> None:
    old_directory = tmp_path / "products"
    old_directory.mkdir(parents=True)

    old_path = old_directory / "imagem-antiga.webp"
    old_path.write_bytes(
        create_image_bytes(
            image_format="WEBP",
        )
    )

    service = ProductImageService(
        upload_directory=tmp_path,
    )

    relative_path = service.save(
        product_code="PRD-000001",
        content=create_image_bytes(),
        content_type="image/png",
        previous_path="products/imagem-antiga.webp",
    )

    assert not old_path.exists()
    assert (tmp_path / relative_path).exists()


def test_removes_existing_product_image(
    tmp_path: Path,
) -> None:
    image_directory = tmp_path / "products"
    image_directory.mkdir(parents=True)

    image_path = image_directory / "produto.webp"
    image_path.write_bytes(
        create_image_bytes(
            image_format="WEBP",
        )
    )

    service = ProductImageService(
        upload_directory=tmp_path,
    )

    service.remove("products/produto.webp")

    assert not image_path.exists()


def test_remove_ignores_missing_image(
    tmp_path: Path,
) -> None:
    service = ProductImageService(
        upload_directory=tmp_path,
    )

    service.remove("products/inexistente.webp")