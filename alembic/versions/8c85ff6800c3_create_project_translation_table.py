"""create project_translation table

Revision ID: 8c85ff6800c3
Revises: 2f13b0c88955
Create Date: 2024-05-04 15:48:30.862389

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c85ff6800c3'
down_revision: Union[str, None] = '2f13b0c88955'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'project_translations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('project_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('language_id', sa.Enum('id', 'en'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_project_translation_project_id", 'project_translations', 'projects',
                        ["project_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('project_translations')
