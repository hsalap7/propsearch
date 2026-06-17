"""Add is_test_data to property table.

Revision ID: 003
Revises: 002
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("properties", sa.Column("is_test_data", sa.Boolean(), server_default="false", nullable=False))
    op.create_index(op.f("ix_properties_is_test_data"), "properties", ["is_test_data"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_properties_is_test_data"), table_name="properties")
    op.drop_column("properties", "is_test_data")
