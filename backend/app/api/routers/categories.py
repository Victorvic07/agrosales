from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_category_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.schemas import CategoryCreate, CategoryRead
from app.modules.categories.service import (
    CategoryAlreadyExistsError,
    CategoryService,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/categories",
    tags=["Categorias"],
)


@router.get(
    "",
    response_model=list[CategoryRead],
)
async def list_categories(
    repository: Annotated[
        CategoryRepository,
        Depends(get_category_repository),
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
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    repository: Annotated[
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
    service = CategoryService(repository)

    try:
        return await service.create(data)
    except CategoryAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error