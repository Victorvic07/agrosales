from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_category_repository,
    get_product_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.categories.repository import CategoryRepository
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductRead
from app.modules.products.service import (
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    ProductService,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/products",
    tags=["Produtos"],
)


@router.get(
    "",
    response_model=list[ProductRead],
)
async def list_products(
    repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> list:
    return await repository.list_all()


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    product_repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
    ],
    category_repository: Annotated[
        CategoryRepository,
        Depends(get_category_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
):
    service = ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
    )

    try:
        return await service.create(data)

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ProductAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error