from fastapi import APIRouter, Query, Response, status

from app.api.deps import DbSession, PaginationDep
from app.schemas.voter import VoterCreate, VoterRead
from app.services import voter_service

router = APIRouter(prefix="/voters", tags=["Votantes"])


@router.post("", response_model=VoterRead, status_code=status.HTTP_201_CREATED,
             summary="Registrar un votante")
def create_voter(data: VoterCreate, db: DbSession):
    return voter_service.create_voter(db, data)


@router.get("", response_model=list[VoterRead], summary="Listar votantes")
def list_voters(
    db: DbSession,
    page: PaginationDep,
    name: str | None = Query(None, description="Filtra por nombre (contiene)"),
    has_voted: bool | None = Query(None, description="Filtra por estado de voto"),
):
    return voter_service.list_voters(db, page.skip, page.limit, name, has_voted)


@router.get("/{voter_id}", response_model=VoterRead, summary="Detalle de un votante")
def get_voter(voter_id: int, db: DbSession):
    return voter_service.get_voter(db, voter_id)


@router.delete("/{voter_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar un votante")
def delete_voter(voter_id: int, db: DbSession):
    voter_service.delete_voter(db, voter_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
