from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Candidate, Vote, Voter
from app.schemas.statistics import CandidateStatistics, VotingStatistics
from app.schemas.vote import VoteCreate


def cast_vote(db: Session, data: VoteCreate) -> Vote:
    """Emite un voto en UNA sola transacción:
    registra el voto, marca has_voted y suma 1 al candidato."""
    # FOR UPDATE bloquea la fila del votante: dos peticiones simultáneas
    # del mismo votante se serializan (en SQLite se ignora).
    voter = db.scalar(select(Voter).where(Voter.id == data.voter_id).with_for_update())
    if voter is None:
        raise NotFoundError(f"Votante {data.voter_id} no encontrado.")

    candidate = db.get(Candidate, data.candidate_id)
    if candidate is None:
        raise NotFoundError(f"Candidato {data.candidate_id} no encontrado.")

    if voter.has_voted:
        raise ConflictError("El votante ya emitió su voto.")

    vote = Vote(voter_id=voter.id, candidate_id=candidate.id)
    voter.has_voted = True
    candidate.votes = Candidate.votes + 1  # incremento atómico en SQL
    db.add(vote)
    try:
        db.commit()
    except IntegrityError:  # red de seguridad: UNIQUE(voter_id)
        db.rollback()
        raise ConflictError("El votante ya emitió su voto.")
    db.refresh(vote)
    return vote


def list_votes(db: Session) -> list[Vote]:
    return list(db.scalars(select(Vote).order_by(Vote.id)))


def get_statistics(db: Session) -> VotingStatistics:
    # Se cuenta desde la tabla votes (fuente de verdad); LEFT JOIN para
    # incluir candidatos con 0 votos.
    rows = db.execute(
        select(Candidate.id, Candidate.name, Candidate.party, func.count(Vote.id))
        .outerjoin(Vote, Vote.candidate_id == Candidate.id)
        .group_by(Candidate.id)
        .order_by(func.count(Vote.id).desc(), Candidate.id)
    ).all()

    total_votes = sum(count for *_, count in rows)
    total_voters = db.scalar(select(func.count(Voter.id)).where(Voter.has_voted.is_(True))) or 0

    candidates = [
        CandidateStatistics(
            candidate_id=cid,
            name=name,
            party=party,
            votes=count,
            percentage=round(count * 100 / total_votes, 2) if total_votes else 0.0,
        )
        for cid, name, party, count in rows
    ]
    return VotingStatistics(
        total_votes=total_votes,
        total_voters_who_voted=total_voters,
        candidates=candidates,
    )
