from pydantic import BaseModel, ConfigDict, Field


class VoteCreate(BaseModel):
    voter_id: int = Field(gt=0, examples=[1])
    candidate_id: int = Field(gt=0, examples=[1])


class VoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    voter_id: int
    candidate_id: int
