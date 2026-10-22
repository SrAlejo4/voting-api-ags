from fastapi import Depends, FastAPI

from app.api.deps import get_current_user
from app.api.routers import auth, candidates, votes, voters
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title="API de Votaciones",
    description=(
        "API RESTful para gestionar votantes, candidatos y votos, "
        "con estadísticas de resultados."
    ),
    version="1.0.0",
)

register_exception_handlers(app)

# /auth/login queda público; el resto exige JWT solo si AUTH_ENABLED=true.
app.include_router(auth.router)
protected = [Depends(get_current_user)]
app.include_router(voters.router, dependencies=protected)
app.include_router(candidates.router, dependencies=protected)
app.include_router(votes.router, dependencies=protected)