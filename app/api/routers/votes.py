from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.schemas.statistics import VotingStatistics
from app.schemas.vote import VoteCreate, VoteRead
from app.services import vote_service

router = APIRouter(prefix="/votes", tags=["Votos"])


@router.post("", response_model=VoteRead, status_code=status.HTTP_201_CREATED,
             summary="Emitir un voto")
def cast_vote(data: VoteCreate, db: DbSession):
    return vote_service.cast_vote(db, data)


@router.get("", response_model=list[VoteRead], summary="Listar todos los votos")
def list_votes(db: DbSession):
    return vote_service.list_votes(db)


@router.get("/statistics", response_model=VotingStatistics,
            summary="Estadísticas de la votación")
def statistics(db: DbSession):
    return vote_service.get_statistics(db)
