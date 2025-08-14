"""create users table

Revision ID: 2aef78992b4d
Revises: 
Create Date: 2025-08-14 16:02:18.933664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aef78992b4d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("email", sa.String(255), unique=True,
                  index=True, nullable=False),
        sa.Column("username", sa.String(50), unique=True,
                  index=True, nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(
            timezone=True), onupdate=sa.func.now()),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    pass
