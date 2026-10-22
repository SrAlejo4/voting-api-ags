from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CedulaStr, LowerEmail, NameStr


class VoterCreate(BaseModel):
    name: NameStr = Field(examples=["Ana Pérez"])
    cedula: CedulaStr = Field(examples=["1234567890"])
    email: LowerEmail = Field(examples=["ana@example.com"])


class VoterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cedula: str
    email: str
    has_voted: bool
