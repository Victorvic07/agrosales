from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_lot_repository,
    get_product_variation_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.lot_schemas import (
    LotCreate,
    LotRead,
    LotStatusUpdate,
    LotUpdate,
)
from app.modules.inventory.lot_service import (
    LotAlreadyExistsError,
    LotEditBlockedError,
    LotNotFoundError,
    LotService,
    LotStatusChangeBlockedError,
    ProductVariationNotFoundError,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/lots",
    tags=["Lotes"],
)


@router.get(
    "",
    response_model=list[LotRead],
)
async def list_lots(
    repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
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
) -> list[LotRead]:
    return await repository.list_all()

@router.get(
    "/{lot_id}",
    response_model=LotRead,
)
async def get_lot_by_id(
    lot_id: UUID,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    lot_repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> LotRead:
    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=current_user.id,
    )

    try:
        return await service.get(lot_id)

    except LotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

@router.put(
    "/{lot_id}",
    response_model=LotRead,
)
async def update_lot(
    lot_id: UUID,
    data: LotUpdate,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    lot_repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> LotRead:
    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=current_user.id,
    )

    try:
        return await service.update(
            lot_id,
            data,
        )

    except LotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (
        LotAlreadyExistsError,
        LotEditBlockedError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error



@router.patch(
    "/{lot_id}/status",
    response_model=LotRead,
)
async def update_lot_status(
    lot_id: UUID,
    data: LotStatusUpdate,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    lot_repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> LotRead:
    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=current_user.id,
    )

    try:
        return await service.change_status(
            lot_id,
            data.status,
        )

    except LotNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except LotStatusChangeBlockedError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

@router.post(
    "",
    response_model=LotRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lot(
    data: LotCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    lot_repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
    ],
    current_user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> LotRead:
    service = LotService(
        session=session,
        lot_repository=lot_repository,
        variation_repository=variation_repository,
        user_id=current_user.id,
    )

    try:
        return await service.create(data)

    except ProductVariationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except LotAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
