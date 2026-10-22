from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.security import create_access_token, verify_admin_credentials

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=Token, summary="Obtener token JWT")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not verify_admin_credentials(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(form.username))
