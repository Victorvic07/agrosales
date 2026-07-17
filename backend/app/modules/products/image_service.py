from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 1200

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class InvalidProductImageError(Exception):
    pass


class ProductImageTooLargeError(Exception):
    pass


class ProductImageService:
    def __init__(
        self,
        upload_directory: Path,
    ) -> None:
        self.upload_directory = upload_directory
        self.product_directory = (
            upload_directory / "products"
        )

    def save(
        self,
        *,
        product_code: str,
        content: bytes,
        content_type: str,
        previous_path: str | None = None,
    ) -> str:
        self._validate_content_type(content_type)
        self._validate_size(content)

        image = self._open_image(content)

        try:
            processed_image = self._prepare_image(image)

            self.product_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            filename = (
                f"{product_code}-{uuid4().hex}.webp"
            )

            relative_path = Path(
                "products",
                filename,
            )

            absolute_path = (
                self.upload_directory / relative_path
            )

            processed_image.save(
                absolute_path,
                format="WEBP",
                quality=85,
                method=6,
            )

        finally:
            image.close()

        if previous_path is not None:
            self.remove(previous_path)

        return relative_path.as_posix()

    def remove(
        self,
        relative_path: str | None,
    ) -> None:
        if not relative_path:
            return

        absolute_path = self._resolve_safe_path(
            relative_path
        )

        if absolute_path.exists():
            absolute_path.unlink()

    def _validate_content_type(
        self,
        content_type: str,
    ) -> None:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidProductImageError(
                "Formato de imagem não permitido"
            )

    def _validate_size(
        self,
        content: bytes,
    ) -> None:
        if len(content) > MAX_IMAGE_SIZE_BYTES:
            raise ProductImageTooLargeError(
                "A imagem não pode ultrapassar 5 MB"
            )

        if not content:
            raise InvalidProductImageError(
                "O arquivo de imagem está vazio"
            )

    def _open_image(
        self,
        content: bytes,
    ) -> Image.Image:
        try:
            image = Image.open(
                BytesIO(content)
            )
            image.load()

        except (
            UnidentifiedImageError,
            OSError,
        ) as error:
            raise InvalidProductImageError(
                "O arquivo enviado não é uma imagem válida"
            ) from error

        return image

    def _prepare_image(
        self,
        image: Image.Image,
    ) -> Image.Image:
        processed_image = image.convert("RGB")

        processed_image.thumbnail(
            (
                MAX_IMAGE_DIMENSION,
                MAX_IMAGE_DIMENSION,
            ),
            Image.Resampling.LANCZOS,
        )

        return processed_image

    def _resolve_safe_path(
        self,
        relative_path: str,
    ) -> Path:
        base_path = self.upload_directory.resolve()

        target_path = (
            self.upload_directory / relative_path
        ).resolve()

        if (
            target_path != base_path
            and base_path not in target_path.parents
        ):
            raise InvalidProductImageError(
                "Caminho de imagem inválido"
            )

        return target_path