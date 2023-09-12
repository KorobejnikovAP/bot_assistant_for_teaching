"""first

Revision ID: 13601d248abe
Revises: 
Create Date: 2023-09-13 01:17:55.261488

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '13601d248abe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=32), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('coach_id', sa.BigInteger(), nullable=True),
    sa.Column('reg_date', sa.DATE(), nullable=True),
    sa.Column('upd_date', sa.DATE(), nullable=True),
    sa.ForeignKeyConstraint(['coach_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('homeworks',
    sa.Column('hw_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('topic', sa.VARCHAR(length=50), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('photo', postgresql.BYTEA(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('hw_id')
    )


def downgrade() -> None:
    op.drop_table('homeworks')
    op.drop_table('users')
