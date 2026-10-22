from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # UNIQUE(voter_id): garantía a nivel de BD de "un voto por votante".
    voter_id: Mapped[int] = mapped_column(
        ForeignKey("voters.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="RESTRICT"), index=True, nullable=False
    )
