from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.modules.users.repository import UserRepository

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_user_repository(session: SessionDependency) -> UserRepository:
    return UserRepository(session)