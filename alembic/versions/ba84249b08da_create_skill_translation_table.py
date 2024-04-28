"""create skill translation table

Revision ID: ba84249b08da
Revises: 6f95ba0d0aa3
Create Date: 2024-04-28 13:19:28.767734

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba84249b08da'
down_revision: Union[str, None] = '6f95ba0d0aa3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'skill_translations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('skill_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(128), unique=False, nullable=False),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('language_id', sa.Enum('id', 'en'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_skill_translation_skill_id", 'skill_translations', 'skills',
                        ["skill_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('skill_translations')