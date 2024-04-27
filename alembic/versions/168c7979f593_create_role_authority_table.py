"""create role_authority table

Revision ID: 168c7979f593
Revises: 8d254635bdf0
Create Date: 2024-04-27 08:03:04.259944

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '168c7979f593'
down_revision: Union[str, None] = '8d254635bdf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'role_authorities',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('role_id', sa.Integer, nullable=True),
        sa.Column('name', sa.String(36), unique=False, nullable=False),
        sa.Column('feature', sa.String(36),  unique=False, nullable=False),
        sa.Column('description', sa.String(256), unique=False, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_role_authority_role_id", 'role_authorities', 'roles',
                        ["role_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('role_authorities')