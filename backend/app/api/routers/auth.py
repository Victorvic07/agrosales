from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.dependencies import get_user_repository
from app.core.security import create_access_token
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    service = UserService(repository)
    user = await service.authenticate(form.username, form.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(
            subject=str(user.id),
            role=user.role,
        )
    )