import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def verify_admin_credentials(username: str, password: str) -> bool:
    """Compara en tiempo constante contra el usuario administrador del .env."""
    user_ok = secrets.compare_digest(username, settings.ADMIN_USERNAME)
    pass_ok = secrets.compare_digest(password, settings.ADMIN_PASSWORD)
    return user_ok and pass_ok


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Devuelve el 'sub' del token o None si es inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
