from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import CedulaStr, NameStr, OptionalTextStr


class CandidateCreate(BaseModel):
    name: NameStr = Field(examples=["Carlos Gómez"])
    cedula: CedulaStr = Field(examples=["1098765432"])
    party: OptionalTextStr = Field(default=None, examples=["Partido Verde"])


class CandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cedula: str
    party: str | None
    votes: int
