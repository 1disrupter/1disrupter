"""add venue_claims table

Revision ID: a1b7c9d0e2f3
Revises: e151932735a3
Create Date: 2026-04-24 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b7c9d0e2f3'
down_revision: Union[str, Sequence[str], None] = ('e151932735a3', '3b8f517ad35d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotent — table may already exist in pods that had Base.metadata.create_all.
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "venue_claims" in insp.get_table_names():
        return
    op.create_table(
        "venue_claims",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("venue_id", sa.String(), sa.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("proof", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("token", sa.String(length=80), nullable=True, unique=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer", sa.String(length=120), nullable=True),
    )
    op.create_index("ix_venue_claims_venue_id", "venue_claims", ["venue_id"])
    op.create_index("ix_venue_claims_email", "venue_claims", ["email"])
    op.create_index("ix_venue_claims_status", "venue_claims", ["status"])


def downgrade() -> None:
    op.drop_index("ix_venue_claims_status", table_name="venue_claims")
    op.drop_index("ix_venue_claims_email", table_name="venue_claims")
    op.drop_index("ix_venue_claims_venue_id", table_name="venue_claims")
    op.drop_table("venue_claims")
