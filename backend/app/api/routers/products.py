from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import (
    get_category_repository,
    get_product_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.categories.repository import CategoryRepository
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreate,
    ProductRead,
    ProductStatusUpdate,
    ProductUpdate,
)
from app.modules.products.service import (
    CategoryNotFoundError,
    InvalidProductPriceError,
    ProductAlreadyExistsError,
    ProductCodeAlreadyExistsError,
    ProductHasDependenciesError,
    ProductNotFoundError,
    ProductService,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/products",
    tags=["Produtos"],
)


def build_product_service(
    product_repository: ProductRepository,
    category_repository: CategoryRepository,
) -> ProductService:
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
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
) -> list[ProductRead]:
    return await repository.list_all()


@router.get(
    "/{product_id}",
    response_model=ProductRead,
)
async def get_product(
    product_id: UUID,
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
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> ProductRead:
    service = build_product_service(
        product_repository,
        category_repository,
    )

    try:
        return await service.get_by_id(product_id)

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


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
) -> ProductRead:
    service = build_product_service(
        product_repository,
        category_repository,
    )

    try:
        return await service.create(data)

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        ProductAlreadyExistsError,
        ProductCodeAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.put(
    "/{product_id}",
    response_model=ProductRead,
)
async def update_product(
    product_id: UUID,
    data: ProductUpdate,
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
) -> ProductRead:
    service = build_product_service(
        product_repository,
        category_repository,
    )

    try:
        return await service.update(
            product_id,
            data,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        ProductAlreadyExistsError,
        ProductCodeAlreadyExistsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except (
        InvalidProductPriceError,
        ValueError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.patch(
    "/{product_id}/status",
    response_model=ProductRead,
)
async def update_product_status(
    product_id: UUID,
    data: ProductStatusUpdate,
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
) -> ProductRead:
    service = build_product_service(
        product_repository,
        category_repository,
    )

    try:
        return await service.update_status(
            product_id,
            data,
        )

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: UUID,
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
            )
        ),
    ],
) -> Response:
    service = build_product_service(
        product_repository,
        category_repository,
    )

    try:
        await service.delete(product_id)

    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except ProductHasDependenciesError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )