"""create school translation table

Revision ID: 8326bdeeca1f
Revises: e19c845faf37
Create Date: 2024-04-27 22:49:00.141026

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8326bdeeca1f'
down_revision: Union[str, None] = 'e19c845faf37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'school_translations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('school_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(128), unique=False, nullable=False),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('address', sa.String(512), unique=False, nullable=True),
        sa.Column('language_id', sa.Enum('id', 'en'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_school_translation_school_id", 'school_translations', 'schools',
                        ["school_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('school_translations')
