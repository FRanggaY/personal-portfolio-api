"""create solution table

Revision ID: c7d23a9d47b5
Revises: b2f6b54e465d
Create Date: 2024-05-04 14:47:24.436193

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d23a9d47b5'
down_revision: Union[str, None] = 'b2f6b54e465d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'solutions',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('image_url', sa.String(512), unique=False, nullable=True),
        sa.Column('logo_url', sa.String(512), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_solution_user_id", 'solutions', 'users',
                        ["user_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('solutions')
