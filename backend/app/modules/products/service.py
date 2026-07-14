from app.modules.categories.repository import CategoryRepository
from app.modules.products.model import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate


class CategoryNotFoundError(Exception):
    pass


class ProductAlreadyExistsError(Exception):
    pass


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.product_repository = product_repository
        self.category_repository = category_repository

    async def create(self, data: ProductCreate) -> Product:
        category = await self.category_repository.get_by_id(
            data.category_id
        )

        if category is None or not category.is_active:
            raise CategoryNotFoundError(
                "Categoria não encontrada ou inativa"
            )

        existing_product = (
            await self.product_repository.get_by_name_and_category(
                data.name,
                data.category_id,
            )
        )

        if existing_product is not None:
            raise ProductAlreadyExistsError(
                "Já existe um produto com esse nome nessa categoria"
            )

        return await self.product_repository.create(data)