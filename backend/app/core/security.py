from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()
JWT_ALGORITHM = "HS256"


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_delta = timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes
    )
    expire_at = datetime.now(UTC) + expire_delta
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload
