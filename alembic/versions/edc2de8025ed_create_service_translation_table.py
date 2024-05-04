"""create service translation table

Revision ID: edc2de8025ed
Revises: c7d23a9d47b5
Create Date: 2024-05-04 14:47:29.938333

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edc2de8025ed'
down_revision: Union[str, None] = 'c7d23a9d47b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'service_translations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('service_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('description', sa.String(512), unique=False, nullable=True),
        sa.Column('language_id', sa.Enum('id', 'en'), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_service_translation_service_id", 'service_translations', 'services',
                        ["service_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('service_translations')