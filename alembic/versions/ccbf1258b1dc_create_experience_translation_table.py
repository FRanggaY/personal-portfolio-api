"""create experience translation table

Revision ID: ccbf1258b1dc
Revises: b3274bb04177
Create Date: 2024-05-02 22:18:51.299692

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccbf1258b1dc'
down_revision: Union[str, None] = 'b3274bb04177'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'experience_translations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('experience_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('employee_type', sa.String(128), unique=False, nullable=False),
        sa.Column('location', sa.String(128), unique=False, nullable=False),
        sa.Column('location_type', sa.String(128), unique=False, nullable=False),
        sa.Column('language_id', sa.Enum('id', 'en'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_experience_translation_experience_id", 'experience_translations', 'experiences',
                        ["experience_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('experience_translations')

