"""create skill table

Revision ID: 6f95ba0d0aa3
Revises: 8326bdeeca1f
Create Date: 2024-04-28 13:19:19.436468

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f95ba0d0aa3'
down_revision: Union[str, None] = '8326bdeeca1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'skills',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('code', sa.String(36), unique=True, nullable=False),
        sa.Column('name', sa.String(128), unique=True, nullable=False),
        sa.Column('image_url', sa.String(512), unique=False, nullable=True),
        sa.Column('logo_url', sa.String(512), unique=False, nullable=True),
        sa.Column('website_url', sa.String(512), unique=False, nullable=True),
        sa.Column('category', sa.String(512), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('skills')
