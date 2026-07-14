from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_inventory_movement_repository,
    get_lot_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.database.session import get_db_session
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.movement_model import InventoryMovement
from app.modules.inventory.movement_repository import (
    InventoryMovementRepository,
)
from app.modules.inventory.movement_schemas import (
    InventoryMovementCreate,
    InventoryMovementRead,
)
from app.modules.inventory.movement_service import (
    InsufficientStockError,
    InventoryMovementService,
)
from app.modules.users.model import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/inventory-movements",
    tags=["Movimentações de estoque"],
)


@router.get(
    "",
    response_model=list[InventoryMovementRead],
)
async def list_inventory_movements(
    repository: Annotated[
        InventoryMovementRepository,
        Depends(get_inventory_movement_repository),
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
    lot_id: UUID | None = Query(default=None),
) -> list[InventoryMovement]:
    if lot_id is not None:
        return await repository.list_by_lot(lot_id)

    return await repository.list_all()


@router.post(
    "",
    response_model=InventoryMovementRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_inventory_movement(
    data: InventoryMovementCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
    lot_repository: Annotated[
        LotRepository,
        Depends(get_lot_repository),
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
) -> InventoryMovement:
    lot = await lot_repository.get_by_id(data.lot_id)

    if lot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado",
        )

    service = InventoryMovementService(session)

    try:
        return await service.register_movement(
            lot=lot,
            user_id=current_user.id,
            movement_type=data.movement_type,
            quantity=data.quantity,
            reason=data.reason,
            notes=data.notes,
        )

    except InsufficientStockError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error