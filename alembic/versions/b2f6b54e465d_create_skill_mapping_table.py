"""create skill mapping table

Revision ID: b2f6b54e465d
Revises: ccbf1258b1dc
Create Date: 2024-05-04 07:52:28.496185

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f6b54e465d'
down_revision: Union[str, None] = 'ccbf1258b1dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'skill_mappings',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('skill_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_skill_mapping_skill_id", 'skill_mappings', 'skills',
                        ["skill_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')
    op.create_foreign_key("fk_skill_mapping_user_id", 'skill_mappings', 'users',
                        ["user_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('skill_mappings')