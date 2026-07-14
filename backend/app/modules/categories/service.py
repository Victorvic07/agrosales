from app.modules.categories.model import Category
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryCreate


class CategoryAlreadyExistsError(Exception):
    pass


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def create(self, data: CategoryCreate) -> Category:
        existing_category = await self.repository.get_by_name(data.name)

        if existing_category is not None:
            raise CategoryAlreadyExistsError(
                "Já existe uma categoria com esse nome"
            )

        return await self.repository.create(data)