from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.variation_model import ProductVariation
from app.modules.products.variation_schemas import ProductVariationCreate


class ProductVariationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        variation_id: UUID,
    ) -> ProductVariation | None:
        return await self.session.get(ProductVariation, variation_id)

    async def get_by_internal_code(
        self,
        internal_code: str,
    ) -> ProductVariation | None:
        statement = select(ProductVariation).where(
            ProductVariation.internal_code == internal_code.strip()
        )
        return await self.session.scalar(statement)

    async def list_all(self) -> list[ProductVariation]:
        statement = select(ProductVariation).order_by(
            ProductVariation.internal_code
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def create(
        self,
        data: ProductVariationCreate,
    ) -> ProductVariation:
        variation = ProductVariation(
            product_id=data.product_id,
            internal_code=data.internal_code.strip(),
            classification=data.classification,
            package_type=data.package_type,
            unit_of_measure=data.unit_of_measure,
            weight_or_volume=data.weight_or_volume,
            standard_price=data.standard_price,
            minimum_price=data.minimum_price,
            minimum_stock=data.minimum_stock,
            commission_percentage=data.commission_percentage,
            barcode=data.barcode,
            qr_code=data.qr_code,
        )

        self.session.add(variation)
        await self.session.commit()
        await self.session.refresh(variation)

        return variation