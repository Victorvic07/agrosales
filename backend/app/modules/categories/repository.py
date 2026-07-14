from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.model import Category
from app.modules.categories.schemas import CategoryCreate


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, category_id: UUID) -> Category | None:
        return await self.session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        statement = select(Category).where(
            Category.name.ilike(name.strip())
        )
        return await self.session.scalar(statement)

    async def list_all(self) -> list[Category]:
        statement = select(Category).order_by(Category.name)
        result = await self.session.scalars(statement)
        return list(result.all())

    async def create(self, data: CategoryCreate) -> Category:
        category = Category(
            name=data.name.strip(),
            description=data.description,
        )

        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)

        return category