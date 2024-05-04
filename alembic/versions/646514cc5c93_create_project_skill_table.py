"""create project_skill table

Revision ID: 646514cc5c93
Revises: 3828b955c48e
Create Date: 2024-05-04 16:28:39.692954

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '646514cc5c93'
down_revision: Union[str, None] = '3828b955c48e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'project_skills',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('project_id', sa.String(36), nullable=True),
        sa.Column('skill_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_project_skill_project_id", 'project_skills', 'projects',
                        ["project_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')
    op.create_foreign_key("fk_project_skill_skill_id", 'project_skills', 'skills',
                        ["skill_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('project_skills')
