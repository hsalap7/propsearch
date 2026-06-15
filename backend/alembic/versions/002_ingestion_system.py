"""Add canonical ingestion, deduplication, geocoding, and observability tables.

Revision ID: 002
Revises: 001
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("properties", sa.Column("fingerprint", sa.String(64), nullable=True))
    op.add_column(
        "properties",
        sa.Column("last_seen_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
    )
    op.alter_column("properties", "bedrooms", existing_type=sa.Integer(), nullable=True)
    op.alter_column("properties", "latitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("properties", "longitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("properties", "location", nullable=True)
    op.create_index("ix_properties_fingerprint", "properties", ["fingerprint"], unique=True)
    op.create_index("ix_properties_last_seen_at", "properties", ["last_seen_at"])

    op.create_table(
        "raw_listings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_raw_listings_source", "raw_listings", ["source"])
    op.create_index("ix_raw_listings_external_id", "raw_listings", ["external_id"])
    op.create_index("ix_raw_listings_created_at", "raw_listings", ["created_at"])

    op.create_table(
        "property_duplicates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column(
            "property_id",
            sa.String(36),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "external_id", name="uq_duplicate_source_external"),
    )
    op.create_index("ix_property_duplicates_source", "property_duplicates", ["source"])
    op.create_index("ix_property_duplicates_fingerprint", "property_duplicates", ["fingerprint"])

    op.create_table(
        "geocode_cache",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("query", sa.Text(), nullable=False, unique=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("raw_response", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "job_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("listings_collected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("listings_saved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("success_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
    )
    op.create_index("ix_job_runs_source", "job_runs", ["source"])
    op.create_index("ix_job_runs_status", "job_runs", ["status"])

    op.create_table(
        "collector_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "job_run_id",
            sa.String(36),
            sa.ForeignKey("job_runs.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_collector_logs_source", "collector_logs", ["source"])
    op.create_index("ix_collector_logs_created_at", "collector_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("collector_logs")
    op.drop_table("job_runs")
    op.drop_table("geocode_cache")
    op.drop_table("property_duplicates")
    op.drop_table("raw_listings")
    op.drop_index("ix_properties_last_seen_at", table_name="properties")
    op.drop_index("ix_properties_fingerprint", table_name="properties")
    op.alter_column(
        "properties",
        "location",
        existing_type=Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )
    op.alter_column("properties", "longitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("properties", "latitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("properties", "bedrooms", existing_type=sa.Integer(), nullable=False)
    op.drop_column("properties", "last_seen_at")
    op.drop_column("properties", "fingerprint")
