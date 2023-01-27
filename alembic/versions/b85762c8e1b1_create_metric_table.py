"""create metric table

Revision ID: b85762c8e1b1
Revises: 
Create Date: 2023-01-27 10:28:05.188252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b85762c8e1b1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column('file_hash', sa.BINARY(16), nullable=False),
        sa.Column('metric_hash', sa.BINARY(16), nullable=False),
        sa.Column('file_name', sa.Unicode(1024), nullable=False),
        sa.Column('group', sa.Unicode(1024), nullable=False),
        sa.Column('metric', sa.Unicode(1024), nullable=False),
        sa.Column('value', sa.Unicode(1024), nullable=False),
        sa.Column("stoplight", sa.SmallInteger, nullable=False),
        sa.Column('metric_timestamp', sa.DateTime, nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('metrics')
