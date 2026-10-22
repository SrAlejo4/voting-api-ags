from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cedula: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    party: Mapped[str | None] = mapped_column(String(100), nullable=True)
    votes: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
