"""add webhook_event_log table

Revision ID: b2c8d3e4f5a6
Revises: a1b7c9d0e2f3
Create Date: 2026-04-24 16:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c8d3e4f5a6'
down_revision: Union[str, None] = 'a1b7c9d0e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "webhook_event_log" in insp.get_table_names():
        return
    op.create_table(
        "webhook_event_log",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("ok", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("error", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("attempts", sa.String(length=8), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_webhook_event_log_type", "webhook_event_log", ["event_type"])
    op.create_index("ix_webhook_event_log_created_at", "webhook_event_log", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_webhook_event_log_created_at", table_name="webhook_event_log")
    op.drop_index("ix_webhook_event_log_type", table_name="webhook_event_log")
    op.drop_table("webhook_event_log")
