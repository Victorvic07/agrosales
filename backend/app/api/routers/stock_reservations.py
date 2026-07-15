from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_product_variation_repository,
    get_reservation_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.modules.inventory.reservation_application_service import (
    ProductVariationNotFoundError,
    ReservationApplicationService,
)
from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.inventory.reservation_schemas import (
    StockReservationRequest,
    StockReservationSummaryRead,
)
from app.modules.inventory.reservation_service import (
    InsufficientAvailableStockError,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/stock-reservations",
    tags=["Reservas de estoque"],
)


@router.post(
    "",
    response_model=StockReservationSummaryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_stock_reservation(
    data: StockReservationRequest,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    reservation_repository: Annotated[
        ReservationRepository,
        Depends(get_reservation_repository),
    ],
    variation_repository: Annotated[
        ProductVariationRepository,
        Depends(get_product_variation_repository),
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
) -> StockReservationSummaryRead:
    service = ReservationApplicationService(
        session=session,
        reservation_repository=reservation_repository,
        variation_repository=variation_repository,
    )

    try:
        return await service.create(data)

    except ProductVariationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except InsufficientAvailableStockError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error