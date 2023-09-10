"""Initial

Revision ID: d683d98c4f1c
Revises: 
Create Date: 2023-09-10 20:27:06.180732

"""
from alembic import op
import sqlalchemy as sa
from db import BaseModel


# revision identifiers, used by Alembic.
revision = 'd683d98c4f1c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(None, 'users', ['user_id'])


def downgrade() -> None:
    op.drop_constraint(None, 'users', type_='unique')
