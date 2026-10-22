import re
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, EmailStr, StringConstraints


def _clean_text(value):
    """Recorta y colapsa espacios internos: '  Ana   Pérez ' -> 'Ana Pérez'."""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return value


def _empty_to_none(value):
    value = _clean_text(value)
    return value or None


NameStr = Annotated[
    str,
    BeforeValidator(_clean_text),
    StringConstraints(min_length=1, max_length=100),
]

OptionalTextStr = Annotated[
    str | None,
    BeforeValidator(_empty_to_none),
    StringConstraints(max_length=100),
]

LowerEmail = Annotated[EmailStr, AfterValidator(lambda v: v.lower())]

def _clean_cedula(value):
    """Acepta '1.234.567.890' o '1 234 567 890' y deja solo los dígitos."""
    if isinstance(value, int):
        value = str(value)
    if isinstance(value, str):
        return re.sub(r"[\s.\-]", "", value)
    return value


CedulaStr = Annotated[
    str,
    BeforeValidator(_clean_cedula),
    StringConstraints(pattern=r"^\d{6,10}$"),
]