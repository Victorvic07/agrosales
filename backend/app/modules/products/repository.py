from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.model import Product
from app.modules.products.schemas import ProductCreate


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_by_name_and_category(
        self,
        name: str,
        category_id: UUID,
    ) -> Product | None:
        statement = select(Product).where(
            Product.name.ilike(name.strip()),
            Product.category_id == category_id,
        )

        return await self.session.scalar(statement)

    async def list_all(self) -> list[Product]:
        statement = select(Product).order_by(Product.name)

        result = await self.session.scalars(statement)

        return list(result.all())

    async def create(self, data: ProductCreate) -> Product:
        product = Product(
            category_id=data.category_id,
            name=data.name.strip(),
            description=data.description,
        )

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        return product