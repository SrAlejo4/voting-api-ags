"""initial schema: voters, candidates, votes

Revision ID: 0001
Revises:
Create Date: 2026-10-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "voters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("cedula", sa.String(10), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("has_voted", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_index("ix_voters_email", "voters", ["email"], unique=True)
    op.create_index("ix_voters_cedula", "voters", ["cedula"], unique=True)

    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("cedula", sa.String(10), nullable=False),
        sa.Column("party", sa.String(100), nullable=True),
        sa.Column("votes", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_candidates_cedula", "candidates", ["cedula"], unique=True)

    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "voter_id",
            sa.Integer(),
            sa.ForeignKey("voters.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("candidates.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_votes_candidate_id", "votes", ["candidate_id"])


def downgrade() -> None:
    op.drop_index("ix_votes_candidate_id", table_name="votes")
    op.drop_table("votes")
    op.drop_table("candidates")
    op.drop_index("ix_voters_email", table_name="voters")
    op.drop_table("voters")
