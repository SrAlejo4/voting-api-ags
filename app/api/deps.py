from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token

DbSession = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class Pagination:
    skip: int
    limit: int


def pagination_params(
    skip: Annotated[int, Query(ge=0, description="Registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo de registros")] = 20,
) -> Pagination:
    return Pagination(skip=skip, limit=limit)


PaginationDep = Annotated[Pagination, Depends(pagination_params)]


def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> str:
    """Si AUTH_ENABLED=false no exige token; si es true valida el JWT."""
    if not settings.AUTH_ENABLED:
        return "anonymous"
    subject = decode_access_token(token) if token else None
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return subject
