"""add auth keys to sessions and pending actions

Revision ID: 9b61f4a0d2c3
Revises: ffa950ed609c
Create Date: 2026-10-06 20:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b61f4a0d2c3"
down_revision: Union[str, Sequence[str], None] = "ffa950ed609c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sessions",
        sa.Column("auth_key", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_sessions_auth_key"),
        "sessions",
        ["auth_key"],
        unique=False,
    )

    op.add_column(
        "pending_actions",
        sa.Column("auth_key", sa.String(length=64), nullable=True),
    )
    op.create_index(
        op.f("ix_pending_actions_auth_key"),
        "pending_actions",
        ["auth_key"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_pending_actions_auth_key"), table_name="pending_actions")
    op.drop_column("pending_actions", "auth_key")
    op.drop_index(op.f("ix_sessions_auth_key"), table_name="sessions")
    op.drop_column("sessions", "auth_key")
