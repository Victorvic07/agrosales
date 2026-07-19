from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_product_repository,
    get_product_variation_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.products.repository import ProductRepository
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)
from app.modules.products.variation_schemas import (
    ProductVariationCreate,
    ProductVariationRead,
    ProductVariationStatusUpdate,
    ProductVariationUpdate,
)
from app.modules.products.variation_service import (
    InvalidMinimumPriceError,
    ProductNotFoundError,
    ProductVariationAlreadyExistsError,
    ProductVariationNotFoundError,
    ProductVariationService,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/product-variations",
    tags=["Variações de produtos"],
)


@router.get(
    "",
    response_model=list[ProductVariationRead],
)
async def list_product_variations(
    repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
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
) -> list[ProductVariationRead]:
    return await repository.list_all()


@router.post(
    "",
    response_model=ProductVariationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_variation(
    data: ProductVariationCreate,
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    product_repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
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
) -> ProductVariationRead:
    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=product_repository,
    )

    try:
        return await service.create(data)
    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ProductVariationAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except InvalidMinimumPriceError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.patch(
    "/{variation_id}",
    response_model=ProductVariationRead,
)
async def update_product_variation(
    variation_id: UUID,
    data: ProductVariationUpdate,
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    product_repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
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
) -> ProductVariationRead:
    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=product_repository,
    )

    try:
        return await service.update(
            variation_id,
            data,
        )
    except ProductVariationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvalidMinimumPriceError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.patch(
    "/{variation_id}/status",
    response_model=ProductVariationRead,
)
async def update_product_variation_status(
    variation_id: UUID,
    data: ProductVariationStatusUpdate,
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    product_repository: Annotated[
        ProductRepository,
        Depends(get_product_repository),
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
) -> ProductVariationRead:
    service = ProductVariationService(
        variation_repository=variation_repository,
        product_repository=product_repository,
    )

    try:
        return await service.update_status(
            variation_id,
            data.is_active,
        )
    except ProductVariationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
