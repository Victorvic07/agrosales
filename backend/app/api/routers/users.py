from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, require_roles
from app.core.enums import UserRole
from app.modules.users.model import User
from app.modules.users.schemas import UserRead

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.get("/admin-check")
async def admin_check(
    _: Annotated[
        User,
        Depends(require_roles(UserRole.ADMINISTRADOR)),
    ],
) -> dict[str, bool]:
    return {"allowed": True}