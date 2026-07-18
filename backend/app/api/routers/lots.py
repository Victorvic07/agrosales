from typing import Annotated

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
from app.modules.inventory.lot_schemas import LotCreate, LotRead
from app.modules.inventory.lot_service import (
    LotAlreadyExistsError,
    LotService,
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
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> list[LotRead]:
    return await repository.list_all()


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
