from pydantic import BaseModel


class CandidateStatistics(BaseModel):
    candidate_id: int
    name: str
    party: str | None
    votes: int
    percentage: float


class VotingStatistics(BaseModel):
    total_votes: int
    total_voters_who_voted: int
    candidates: list[CandidateStatistics]
