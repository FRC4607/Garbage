"""add columns for log datetime, event, and match level/number

Revision ID: f59f1ff85c3e
Revises: b85762c8e1b1
Create Date: 2023-02-01 16:53:28.437365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f59f1ff85c3e"
down_revision = "b85762c8e1b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("metrics", sa.Column("log_timestamp", sa.DateTime))
    op.add_column("metrics", sa.Column("event_key", sa.Unicode(256)))
    op.add_column("metrics", sa.Column("match_info", sa.Unicode(16)))


def downgrade() -> None:
    op.drop_column("metrics", "match_info")
    op.drop_column("metrics", "event_key")
    op.drop_column("metrics", "log_timestamp")
