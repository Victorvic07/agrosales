from typing import Protocol

from app.core.security import verify_password
from app.modules.users.model import User


class UserReader(Protocol):
    async def get_by_email(self, email: str) -> User | None: ...


class UserService:
    def __init__(self, repository: UserReader) -> None:
        self.repository = repository

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.repository.get_by_email(email.lower())

        if user is None or not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user