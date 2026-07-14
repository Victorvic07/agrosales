from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.enums import UserRole

password_hasher = PasswordHash.recommended()


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: datetime


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(subject: str, role: UserRole) -> str:
    settings = get_settings()

    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "role": role.value,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    return TokenPayload.model_validate(payload)