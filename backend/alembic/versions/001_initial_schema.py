"""Initial migration - create properties table with PostGIS support.

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create properties table."""
    op.create_table(
        "properties",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("property_type", sa.String(50), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column("price_per_sqft", sa.Numeric(), nullable=True),
        sa.Column("area_sqft", sa.Integer(), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=False),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("locality", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("location", Geography("POINT", 4326), nullable=False),
        sa.Column("listing_url", sa.Text(), nullable=False),
        sa.Column("image_urls", sa.JSON(), nullable=True),
        sa.Column("amenities", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("listing_url"),
    )
    op.create_index(op.f("ix_properties_source"), "properties", ["source"], unique=False)
    op.create_index(op.f("ix_properties_external_id"), "properties", ["external_id"], unique=False)
    op.create_index(op.f("ix_properties_property_type"), "properties", ["property_type"], unique=False)
    op.create_index(op.f("ix_properties_price"), "properties", ["price"], unique=False)
    op.create_index(op.f("ix_properties_bedrooms"), "properties", ["bedrooms"], unique=False)
    op.create_index(op.f("ix_properties_locality"), "properties", ["locality"], unique=False)
    op.create_index("ix_properties_location", "properties", ["location"], unique=False, postgresql_using="gist")


def downgrade() -> None:
    """Drop properties table."""
    op.drop_table("properties")
