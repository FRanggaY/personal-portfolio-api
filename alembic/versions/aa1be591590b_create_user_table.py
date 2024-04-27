"""create user table

Revision ID: aa1be591590b
Revises: 168c7979f593
Create Date: 2024-04-27 08:03:33.492380

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa1be591590b'
down_revision: Union[str, None] = '168c7979f593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True, server_default=str(uuid.uuid4())),
        sa.Column('role_id', sa.Integer, nullable=True),
        sa.Column('username', sa.String(36), unique=True, nullable=False),
        sa.Column('email', sa.String(256),  unique=True, nullable=False),
        sa.Column('name', sa.String(128), unique=False, nullable=True),
        sa.Column('image_url', sa.String(512), unique=False, nullable=True),
        sa.Column('password', sa.String(512), unique=False, nullable=False),
        sa.Column('no_handphone', sa.String(256), unique=False, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('gender', sa.Enum('male', 'female'), nullable=True),
        sa.Column('last_login_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.NOW(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.NOW(), onupdate=sa.func.NOW(), nullable=False),
    )
    op.create_foreign_key("fk_user_role_id", 'users', 'roles',
                        ["role_id"], ["id"], ondelete='CASCADE', onupdate='CASCADE')

def downgrade() -> None:
    op.drop_table('users')