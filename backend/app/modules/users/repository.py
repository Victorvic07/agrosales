from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower())
        return await self.session.scalar(statement)

    async def create(self, data: UserCreate) -> User:
        user = User(
            name=data.name,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            role=data.role,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user