"""create school table

Revision ID: e19c845faf37
Revises: 2753d2bb6e99
Create Date: 2024-04-27 22:48:41.863475

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e19c845faf37'
down_revision: Union[str, None] = '2753d2bb6e99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'schools',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('code', sa.String(36), unique=True, nullable=False),
        sa.Column('name', sa.String(128), unique=True, nullable=False),
        sa.Column('image_url', sa.String(512), unique=False, nullable=True),
        sa.Column('logo_url', sa.String(512), unique=False, nullable=True),
        sa.Column('website_url', sa.String(512), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('schools')

