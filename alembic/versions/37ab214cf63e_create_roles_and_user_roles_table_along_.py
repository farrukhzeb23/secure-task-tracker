"""create roles and user_roles table along with default roles

Revision ID: 37ab214cf63e
Revises: d5a4b1fd5cd8
Create Date: 2025-08-23 21:57:36.625932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = '37ab214cf63e'
down_revision: Union[str, Sequence[str], None] = 'd5a4b1fd5cd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "name",
            sa.String(50),
            unique=True,
            index=True,
            nullable=False
        ),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.func.now()
        ),
    )

    op.create_table(
        "user_roles",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.UUID,
            sa.ForeignKey("users.id"),
            nullable=False
        ),
        sa.Column(
            "role_id",
            sa.UUID,
            sa.ForeignKey("roles.id"),
            nullable=False
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
    )

    # Insert default roles
    op.execute("""
        INSERT INTO roles (id, name, description) VALUES 
        (gen_random_uuid(), 'admin', 'Administrator with full access'),
        (gen_random_uuid(), 'user', 'Regular user with limited access')
    """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_roles")
    op.drop_table("roles")
    pass
