import asyncio
import os

import app.database.models  # noqa: F401
from app.core.enums import UserRole
from app.database.session import async_session_factory
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate


async def ensure_admin_exists(
    repository: UserRepository,
    name: str,
    email: str,
    password: str,
) -> bool:
    existing_user = await repository.get_by_email(email)

    if existing_user is not None:
        return False

    await repository.create(
        UserCreate(
            name=name,
            email=email,
            password=password,
            role=UserRole.ADMINISTRADOR,
        )
    )

    return True


async def main() -> None:
    name = os.environ["ADMIN_NAME"]
    email = os.environ["ADMIN_EMAIL"]
    password = os.environ["ADMIN_PASSWORD"]

    async with async_session_factory() as session:
        repository = UserRepository(session)

        created = await ensure_admin_exists(
            repository=repository,
            name=name,
            email=email,
            password=password,
        )

    if created:
        print("Administrador criado.")
    else:
        print("Administrador já existe.")


if __name__ == "__main__":
    asyncio.run(main())