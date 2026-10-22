from sqlalchemy import Boolean, String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Voter(Base):
    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cedula: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    has_voted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
