import uuid
"""create refresh token table

Revision ID: d5a4b1fd5cd8
Revises: 2aef78992b4d
Create Date: 2025-08-23 15:44:45.131003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5a4b1fd5cd8'
down_revision: Union[str, Sequence[str], None] = '2aef78992b4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.UUID, sa.ForeignKey(
            "users.id"), nullable=False),
        sa.Column("token_hash", sa.String, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("refresh_token")
    pass
