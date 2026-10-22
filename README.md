# API de Votaciones (FastAPI + PostgreSQL)

API RESTful para gestionar votantes, candidatos y votos, con estadísticas de resultados.

**Stack:** Python 3.12+, FastAPI, SQLAlchemy 2, PostgreSQL 16, Alembic, JWT.

## Estructura

```
app/
├── main.py              # App FastAPI, routers y manejo de errores
├── core/                # config, conexión a BD, seguridad JWT, excepciones
├── models/              # Modelos SQLAlchemy (tablas)
├── schemas/             # Esquemas Pydantic (validación de entrada/salida)
├── services/            # Lógica de negocio y validaciones
└── api/
    ├── deps.py          # Dependencias: sesión BD, paginación, auth
    └── routers/         # Endpoints: voters, candidates, votes, auth
alembic/                 # Migraciones de la base de datos
```

## Ejecutar localmente
Abrir una terminal bash (Git Bash u otra) y ejecutar el siguiente comando (todas las lineas en la misma ejecución) en el directorio del proyecto. Este ejecutará la API localmente, a la cual se puede acceder con los URL's para el Swagger UI y creará la base de datos PostgreSQL (Pedirá clave de accceso del PostgreSQL local).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
psql -U postgres -c "CREATE USER voting_user WITH PASSWORD 'voting_pass';"
psql -U postgres -c "CREATE DATABASE voting_db OWNER voting_user;"
alembic upgrade head
uvicorn app.main:app --reload
```
- Swagger UI: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Descripción | Códigos |
|---|---|---|---|
| POST | `/voters` | Registrar votante | 201, 409, 422 |
| GET | `/voters` | Listar (`skip`, `limit`, `name`, `has_voted`) | 200 |
| GET | `/voters/{id}` | Detalle | 200, 404 |
| DELETE | `/voters/{id}` | Eliminar | 204, 404, 409 |
| POST | `/candidates` | Registrar candidato | 201, 409, 422 |
| GET | `/candidates` | Listar (`skip`, `limit`, `name`, `party`) | 200 |
| GET | `/candidates/{id}` | Detalle | 200, 404 |
| DELETE | `/candidates/{id}` | Eliminar | 204, 404, 409 |
| POST | `/votes` | Emitir voto | 201, 404, 409, 422 |
| GET | `/votes` | Listar votos | 200 |
| GET | `/votes/statistics` | Estadísticas | 200 |
| POST | `/auth/login` | Token JWT (opcional) | 200, 401 |

## Ejemplos con curl

```bash
# Registrar votantes
curl -X POST localhost:8000/voters -H "Content-Type: application/json" \
  -d '{"name": "Ana Pérez", "cedula": 92326789, "email": "ana@example.com"}'
curl -X POST localhost:8000/voters -H "Content-Type: application/json" \
  -d '{"name": "Luis Torres", "cedula": 786512, "email": "luis@example.com"}'

# Registrar candidatos
curl -X POST localhost:8000/candidates -H "Content-Type: application/json" \
  -d '{"name": "Carlos Gómez", "cedula": 213265, "party": "Partido Verde"}'
curl -X POST localhost:8000/candidates -H "Content-Type: application/json" \
  -d '{"name": "María Ruiz", "cedula": 216578, "party": "Partido Azul"}'

# Listar con filtros y paginación
curl "localhost:8000/voters?skip=0&limit=10&has_voted=false"
curl "localhost:8000/candidates?party=verde"

# Emitir votos
curl -X POST localhost:8000/votes -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 1}'
curl -X POST localhost:8000/votes -H "Content-Type: application/json" \
  -d '{"voter_id": 2, "candidate_id": 1}'

# Doble voto -> 409
curl -X POST localhost:8000/votes -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 2}'

# Estadísticas
curl localhost:8000/votes/statistics
```

Respuesta de ejemplo de `/votes/statistics`:
```json
{
  "total_votes": 2,
  "total_voters_who_voted": 2,
  "candidates": [
    {"candidate_id": 1, "name": "Carlos Gómez", "cedula": 213265, "party": "Partido Verde", "votes": 2, "percentage": 100.0},
    {"candidate_id": 2, "name": "María Ruiz", "cedula": 213265, "party": "Partido Azul", "votes": 0, "percentage": 0.0}
  ]
}
```

### Capturas de las estadísticas

<img width="1742" height="565" alt="voting-api" src="https://github.com/user-attachments/assets/01407482-e488-4613-b4eb-7730a4d830b0" />

## Autenticación JWT

```bash
TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -d "username=admin&password=admin123" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl localhost:8000/voters -H "Authorization: Bearer $TOKEN"
```
En Swagger usa el botón **Authorize**.

## Decisiones de diseño

- **Votante vs. candidato:** La regla "un votante no puede ser candidato (y viceversa)" se valida por cédula, que es única en cada tabla y se comprueba en ambos sentidos.
- **Un voto por votante:** se valida en el servicio y además hay una restricción `UNIQUE(voter_id)` en la tabla `votes`. Se bloquea la fila del votante (`SELECT ... FOR UPDATE`) para que peticiones concurrentes no dupliquen el voto.
- **Integridad:** emitir un voto registra el `Vote`, marca `has_voted` y suma 1 a `candidates.votes` en **una sola transacción**.
- **Eliminaciones:** no se puede eliminar un votante que ya votó ni un candidato con votos (`409`), para no alterar las estadísticas.
- **Estadísticas:** se calculan desde la tabla `votes` (fuente de verdad), incluyen candidatos con 0 votos y evitan la división por cero.
