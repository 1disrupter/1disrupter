"""add referral_credits to user_wallets

Revision ID: c3d4e5f60001
Revises: b2c8d3e4f5a6
Create Date: 2026-04-28 13:50:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f60001"
down_revision = "b2c8d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Lifetime referral credits received by this wallet. Lets us compute
    # "you've invited N friends" without a full event ledger.
    op.add_column(
        "user_wallets",
        sa.Column(
            "referral_credits",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("user_wallets", "referral_credits")
