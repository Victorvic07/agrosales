from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.model import Product
from app.modules.products.schemas import ProductCreate


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        product_id: UUID,
    ) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_code(
        self,
        code: str,
    ) -> Product | None:
        statement = select(Product).where(
            Product.code == code.strip(),
        )

        return await self.session.scalar(statement)

    async def exists_by_code(
        self,
        code: str,
    ) -> bool:
        statement = select(Product.id).where(
            Product.code == code.strip(),
        )

        product_id = await self.session.scalar(statement)

        return product_id is not None

    async def get_last_generated_code(
        self,
    ) -> str | None:
        statement = (
            select(Product.code)
            .where(Product.code.like("PRD-%"))
            .order_by(Product.code.desc())
            .limit(1)
        )

        return await self.session.scalar(statement)

    async def get_by_name_and_category(
        self,
        name: str,
        category_id: UUID | None,
    ) -> Product | None:
        statement = select(Product).where(
            Product.name.ilike(name.strip()),
            Product.category_id == category_id,
        )

        return await self.session.scalar(statement)

    async def list_all(self) -> list[Product]:
        statement = select(Product).order_by(
            Product.name,
        )

        result = await self.session.scalars(statement)

        return list(result.all())

    async def create(
        self,
        data: ProductCreate,
        code: str,
    ) -> Product:
        product = Product(
            category_id=data.category_id,
            code=code,
            name=data.name,
            unit=data.unit,
            custom_unit=data.custom_unit,
            cost_price=data.cost_price,
            standard_price=data.standard_price,
            minimum_price=data.minimum_price,
            short_description=data.short_description,
            detailed_description=data.detailed_description,
            internal_notes=data.internal_notes,
            status=data.status,
        )

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product