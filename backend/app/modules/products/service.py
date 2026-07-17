from decimal import Decimal
from uuid import UUID

from app.modules.categories.repository import CategoryRepository
from app.modules.products.code_generator import (
    generate_unique_product_code,
)
from app.modules.products.enums import ProductUnit
from app.modules.products.model import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreate,
    ProductStatusUpdate,
    ProductUpdate,
)


class CategoryNotFoundError(Exception):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductCodeAlreadyExistsError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class ProductHasDependenciesError(Exception):
    pass


class InvalidProductPriceError(Exception):
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
        await self._validate_category_id(data.category_id)
        await self._validate_duplicate_name(
            name=data.name,
            category_id=data.category_id,
        )

        code = await self._resolve_product_code(data)

        return await self.product_repository.create(
            data,
            code,
        )

    async def get_by_id(
        self,
        product_id: UUID,
    ) -> Product:
        product = await self.product_repository.get_by_id(
            product_id
        )

        if product is None:
            raise ProductNotFoundError(
                "Produto não encontrado"
            )

        return product

    async def update(
        self,
        product_id: UUID,
        data: ProductUpdate,
    ) -> Product:
        product = await self.get_by_id(product_id)

        changes = data.model_dump(exclude_unset=True)

        await self._prepare_update_changes(
            product,
            changes,
        )

        return await self.product_repository.update(
            product,
            changes,
        )

    async def update_status(
        self,
        product_id: UUID,
        data: ProductStatusUpdate,
    ) -> Product:
        product = await self.get_by_id(product_id)

        return await self.product_repository.update_status(
            product,
            data.status,
        )

    async def delete(
        self,
        product_id: UUID,
    ) -> None:
        product = await self.get_by_id(product_id)

        has_variations = (
            await self.product_repository.has_variations(
                product_id
            )
        )

        if has_variations:
            raise ProductHasDependenciesError(
                "O produto não pode ser excluído porque "
                "possui variações vinculadas"
            )

        await self.product_repository.delete(product)

    async def _prepare_update_changes(
        self,
        product: Product,
        changes: dict,
    ) -> None:
        if "category_id" in changes:
            await self._validate_category_id(
                changes["category_id"]
            )

        if "code" in changes:
            code = changes["code"]

            if code is None:
                raise ValueError(
                    "O código do produto não pode ser vazio"
                )

            normalized_code = code.strip().upper()
            changes["code"] = normalized_code

            existing_by_code = (
                await self.product_repository.get_by_code(
                    normalized_code
                )
            )

            if (
                existing_by_code is not None
                and existing_by_code.id != product.id
            ):
                raise ProductCodeAlreadyExistsError(
                    "Já existe um produto com esse código"
                )

        final_name = changes.get(
            "name",
            product.name,
        )
        final_category_id = changes.get(
            "category_id",
            product.category_id,
        )

        if (
            "name" in changes
            or "category_id" in changes
        ):
            existing_by_name = (
                await self.product_repository
                .get_by_name_and_category(
                    final_name,
                    final_category_id,
                )
            )

            if (
                existing_by_name is not None
                and existing_by_name.id != product.id
            ):
                raise ProductAlreadyExistsError(
                    "Já existe um produto com esse nome "
                    "nessa categoria"
                )

        final_standard_price = changes.get(
            "standard_price",
            product.standard_price,
        )
        final_minimum_price = changes.get(
            "minimum_price",
            product.minimum_price,
        )

        self._validate_final_prices(
            standard_price=final_standard_price,
            minimum_price=final_minimum_price,
        )

        final_unit = changes.get(
            "unit",
            product.unit,
        )
        final_custom_unit = changes.get(
            "custom_unit",
            product.custom_unit,
        )

        self._validate_final_unit(
            unit=final_unit,
            custom_unit=final_custom_unit,
        )

    async def _validate_category_id(
        self,
        category_id: UUID | None,
    ) -> None:
        if category_id is None:
            return

        category = await self.category_repository.get_by_id(
            category_id
        )

        if category is None or not category.is_active:
            raise CategoryNotFoundError(
                "Categoria não encontrada ou inativa"
            )

    async def _validate_duplicate_name(
        self,
        name: str,
        category_id: UUID | None,
    ) -> None:
        existing_product = (
            await self.product_repository.get_by_name_and_category(
                name,
                category_id,
            )
        )

        if existing_product is not None:
            raise ProductAlreadyExistsError(
                "Já existe um produto com esse nome "
                "nessa categoria"
            )

    def _validate_final_prices(
        self,
        standard_price: Decimal,
        minimum_price: Decimal,
    ) -> None:
        if minimum_price > standard_price:
            raise InvalidProductPriceError(
                "O preço mínimo não pode ser maior "
                "que o preço padrão"
            )

    def _validate_final_unit(
        self,
        unit: ProductUnit,
        custom_unit: str | None,
    ) -> None:
        if (
            unit == ProductUnit.OUTRO
            and not custom_unit
        ):
            raise ValueError(
                "A unidade personalizada é obrigatória "
                "quando a unidade for OUTRO"
            )

        if (
            unit != ProductUnit.OUTRO
            and custom_unit is not None
        ):
            raise ValueError(
                "A unidade personalizada só pode ser informada "
                "quando a unidade for OUTRO"
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