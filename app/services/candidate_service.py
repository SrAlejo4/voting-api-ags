from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Candidate, Voter
from app.schemas.candidate import CandidateCreate


def create_candidate(db: Session, data: CandidateCreate) -> Candidate:
    # Regla cruzada: la cédula identifica a la persona.
    if db.scalar(select(Voter.id).where(Voter.cedula == data.cedula)) is not None:
        raise ConflictError(
            "Esta cédula ya está registrada como votante; no puede ser candidato."
        )
    if db.scalar(select(Candidate.id).where(Candidate.cedula == data.cedula)) is not None:
        raise ConflictError("Ya existe un candidato con esa cédula.")

    candidate = Candidate(name=data.name, cedula=data.cedula, party=data.party)
    db.add(candidate)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Ya existe un candidato con esa cédula.")
    db.refresh(candidate)
    return candidate


def list_candidates(
    db: Session,
    skip: int,
    limit: int,
    name: str | None = None,
    party: str | None = None,
) -> list[Candidate]:
    stmt = select(Candidate).order_by(Candidate.id).offset(skip).limit(limit)
    if name:
        stmt = stmt.where(Candidate.name.ilike(f"%{name}%"))
    if party:
        stmt = stmt.where(Candidate.party.ilike(f"%{party}%"))
    return list(db.scalars(stmt))


def get_candidate(db: Session, candidate_id: int) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise NotFoundError(f"Candidato {candidate_id} no encontrado.")
    return candidate


def delete_candidate(db: Session, candidate_id: int) -> None:
    candidate = get_candidate(db, candidate_id)
    if candidate.votes > 0:
        raise ConflictError(
            "No se puede eliminar un candidato que ya recibió votos (alteraría las estadísticas)."
        )
    db.delete(candidate)
    db.commit()
