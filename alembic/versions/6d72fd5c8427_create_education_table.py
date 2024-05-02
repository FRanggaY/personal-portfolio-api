"""create education table

Revision ID: 6d72fd5c8427
Revises: ba84249b08da
Create Date: 2024-05-02 21:23:47.507081

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d72fd5c8427'
down_revision: Union[str, None] = 'ba84249b08da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'educations',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('school_id', sa.String(36), nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(128), unique=False, nullable=False),
        sa.Column('started_at', sa.Date, nullable=False),
        sa.Column('finished_at', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_education_school_id", 'educations', 'schools',
                        ["school_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')
    op.create_foreign_key("fk_education_user_id", 'educations', 'users',
                        ["user_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('educations')
