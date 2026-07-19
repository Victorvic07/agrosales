from decimal import Decimal
from uuid import UUID

from app.modules.products.enums import ProductStatus
from app.modules.products.repository import ProductRepository
from app.modules.products.variation_model import ProductVariation
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)
from app.modules.products.variation_schemas import (
    ProductVariationCreate,
    ProductVariationUpdate,
)


class ProductNotFoundError(Exception):
    pass


class ProductVariationAlreadyExistsError(Exception):
    pass


class InvalidMinimumPriceError(Exception):
    pass


class ProductVariationNotFoundError(Exception):
    pass


class ProductVariationService:
    def __init__(
        self,
        variation_repository: ProductVariationRepository,
        product_repository: ProductRepository,
    ) -> None:
        self.variation_repository = variation_repository
        self.product_repository = product_repository

    async def create(
        self,
        data: ProductVariationCreate,
    ) -> ProductVariation:
        product = await self.product_repository.get_by_id(
            data.product_id
        )

        if (
            product is None
            or product.status != ProductStatus.ATIVO
        ):
            raise ProductNotFoundError(
                "Produto não encontrado ou inativo"
            )

        existing = (
            await self.variation_repository.get_by_internal_code(
                data.internal_code
            )
        )

        if existing is not None:
            raise ProductVariationAlreadyExistsError(
                "Já existe uma variação com esse código interno"
            )

        if data.minimum_price > data.standard_price:
            raise InvalidMinimumPriceError(
                "O preço mínimo não pode ser maior que o preço padrão"
            )

        return await self.variation_repository.create(data)

    async def update(
        self,
        variation_id: UUID,
        data: ProductVariationUpdate,
    ) -> ProductVariation:
        variation = (
            await self.variation_repository.get_by_id(
                variation_id
            )
        )

        if variation is None:
            raise ProductVariationNotFoundError(
                "Variação de produto não encontrada"
            )

        standard_price = (
            data.standard_price
            if data.standard_price is not None
            else Decimal(variation.standard_price)
        )
        minimum_price = (
            data.minimum_price
            if data.minimum_price is not None
            else Decimal(variation.minimum_price)
        )

        if minimum_price > standard_price:
            raise InvalidMinimumPriceError(
                "O preço mínimo não pode ser maior que o preço padrão"
            )

        return await self.variation_repository.update(
            variation,
            data,
        )

    async def update_status(
        self,
        variation_id: UUID,
        is_active: bool,
    ) -> ProductVariation:
        variation = (
            await self.variation_repository.get_by_id(
                variation_id
            )
        )

        if variation is None:
            raise ProductVariationNotFoundError(
                "Variação de produto não encontrada"
            )

        return await self.variation_repository.update_status(
            variation,
            is_active,
        )
