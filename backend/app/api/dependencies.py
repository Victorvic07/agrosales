from collections.abc import Callable
from typing import Annotated
from uuid import UUID
from app.modules.products.repository import ProductRepository
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.categories.repository import CategoryRepository
from app.core.config import get_settings
from app.core.enums import UserRole
from app.core.security import decode_access_token
from app.database.session import get_db_session
from app.modules.users.model import User
from app.modules.inventory.lot_repository import LotRepository
from app.modules.users.repository import UserRepository
from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.movement_repository import (
    InventoryMovementRepository,
)
from app.modules.products.variation_repository import (
    ProductVariationRepository,
)




settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login"
)

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: SessionDependency) -> UserRepository:
    return UserRepository(session)


def get_category_repository(
    session: SessionDependency,
) -> CategoryRepository:
    return CategoryRepository(session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDependency,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = UUID(payload.sub)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception from None

    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    async def dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para esta ação",
            )

        return current_user

    return dependency

def get_product_repository(
    session: SessionDependency,
) -> ProductRepository:
    return ProductRepository(session)

def get_product_variation_repository(
    session: SessionDependency,
) -> ProductVariationRepository:
    return ProductVariationRepository(session)

def get_lot_repository(
    session: SessionDependency,
) -> LotRepository:
    return LotRepository(session)

def get_inventory_movement_repository(
    session: SessionDependency,
) -> InventoryMovementRepository:
    return InventoryMovementRepository(session)