from app.modules.categories.repository import CategoryRepository
from app.modules.products.code_generator import (
    generate_unique_product_code,
)
from app.modules.products.model import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate


class CategoryNotFoundError(Exception):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductCodeAlreadyExistsError(Exception):
    pass


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.product_repository = product_repository
        self.category_repository = category_repository

    async def create(
        self,
        data: ProductCreate,
    ) -> Product:
        await self._validate_category(data)
        await self._validate_duplicate_name(data)

        code = await self._resolve_product_code(data)

        return await self.product_repository.create(
            data,
            code,
        )

    async def _validate_category(
        self,
        data: ProductCreate,
    ) -> None:
        if data.category_id is None:
            return

        category = await self.category_repository.get_by_id(
            data.category_id
        )

        if category is None or not category.is_active:
            raise CategoryNotFoundError(
                "Categoria não encontrada ou inativa"
            )

    async def _validate_duplicate_name(
        self,
        data: ProductCreate,
    ) -> None:
        existing_product = (
            await self.product_repository.get_by_name_and_category(
                data.name,
                data.category_id,
            )
        )

        if existing_product is not None:
            raise ProductAlreadyExistsError(
                "Já existe um produto com esse nome "
                "nessa categoria"
            )

    async def _resolve_product_code(
        self,
        data: ProductCreate,
    ) -> str:
        if data.code is None:
            return await generate_unique_product_code(
                self.product_repository
            )

        code = data.code.strip().upper()

        if await self.product_repository.exists_by_code(code):
            raise ProductCodeAlreadyExistsError(
                "Já existe um produto com esse código"
            )

        return code