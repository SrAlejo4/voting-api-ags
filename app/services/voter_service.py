from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Candidate, Voter
from app.schemas.voter import VoterCreate


def create_voter(db: Session, data: VoterCreate) -> Voter:
    # Regla cruzada: la cédula identifica a la persona.
    if db.scalar(select(Candidate.id).where(Candidate.cedula == data.cedula)) is not None:
        raise ConflictError(
            "Esta cédula ya está registrada como candidato; no puede ser votante."
        )
    if db.scalar(select(Voter.id).where(Voter.cedula == data.cedula)) is not None:
        raise ConflictError("Ya existe un votante con esa cédula.")
    if db.scalar(select(Voter.id).where(Voter.email == data.email)) is not None:
        raise ConflictError("Ya existe un votante con ese correo electrónico.")

    voter = Voter(name=data.name, cedula=data.cedula, email=data.email)
    db.add(voter)
    try:
        db.commit()
    except IntegrityError:  # condición de carrera sobre cédula/email únicos
        db.rollback()
        raise ConflictError("Ya existe un votante con ese correo electrónico o cédula.")
    db.refresh(voter)
    return voter


def list_voters(
    db: Session,
    skip: int,
    limit: int,
    name: str | None = None,
    has_voted: bool | None = None,
) -> list[Voter]:
    stmt = select(Voter).order_by(Voter.id).offset(skip).limit(limit)
    if name:
        stmt = stmt.where(Voter.name.ilike(f"%{name}%"))
    if has_voted is not None:
        stmt = stmt.where(Voter.has_voted == has_voted)
    return list(db.scalars(stmt))


def get_voter(db: Session, voter_id: int) -> Voter:
    voter = db.get(Voter, voter_id)
    if voter is None:
        raise NotFoundError(f"Votante {voter_id} no encontrado.")
    return voter


def delete_voter(db: Session, voter_id: int) -> None:
    voter = get_voter(db, voter_id)
    if voter.has_voted:
        raise ConflictError(
            "No se puede eliminar un votante que ya emitió su voto (alteraría las estadísticas)."
        )
    db.delete(voter)
    db.commit()
