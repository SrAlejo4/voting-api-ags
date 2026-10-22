from fastapi import APIRouter, Query, Response, status

from app.api.deps import DbSession, PaginationDep
from app.schemas.candidate import CandidateCreate, CandidateRead
from app.services import candidate_service

router = APIRouter(prefix="/candidates", tags=["Candidatos"])


@router.post("", response_model=CandidateRead, status_code=status.HTTP_201_CREATED,
             summary="Registrar un candidato")
def create_candidate(data: CandidateCreate, db: DbSession):
    return candidate_service.create_candidate(db, data)


@router.get("", response_model=list[CandidateRead], summary="Listar candidatos")
def list_candidates(
    db: DbSession,
    page: PaginationDep,
    name: str | None = Query(None, description="Filtra por nombre (contiene)"),
    party: str | None = Query(None, description="Filtra por partido (contiene)"),
):
    return candidate_service.list_candidates(db, page.skip, page.limit, name, party)


@router.get("/{candidate_id}", response_model=CandidateRead, summary="Detalle de un candidato")
def get_candidate(candidate_id: int, db: DbSession):
    return candidate_service.get_candidate(db, candidate_id)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar un candidato")
def delete_candidate(candidate_id: int, db: DbSession):
    candidate_service.delete_candidate(db, candidate_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
