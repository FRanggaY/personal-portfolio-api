"""create role table

Revision ID: 8d254635bdf0
Revises: 
Create Date: 2024-04-27 08:02:14.712914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d254635bdf0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(36), unique=True, nullable=False),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('name', sa.String(126), unique=True, nullable=False),
        sa.Column('description', sa.String(256), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('roles')
