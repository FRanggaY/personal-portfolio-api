"""create project_attachment table

Revision ID: 3828b955c48e
Revises: 8c85ff6800c3
Create Date: 2024-05-04 16:02:41.284648

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3828b955c48e'
down_revision: Union[str, None] = '8c85ff6800c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'project_attachments',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('project_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('image_url', sa.String(512), unique=False, nullable=True),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('website_url', sa.String(512), unique=False, nullable=True),
        sa.Column('category', sa.String(512), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_project_attachment_project_id", 'project_attachments', 'projects',
                        ["project_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('project_attachments')

