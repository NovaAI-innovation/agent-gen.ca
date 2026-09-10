"""v2 catalog states — listing/release/creator state machines and audit tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Listing state column ──────────────────────────────────────────────
    op.add_column(
        "listings",
        sa.Column("state", sa.String(30), nullable=False, server_default="draft"),
    )
    # Migrate existing data: is_published=true → state='published'
    op.execute("UPDATE listings SET state = 'published' WHERE is_published = true")
    op.execute("UPDATE listings SET state = 'draft' WHERE is_published = false")
    op.drop_column("listings", "is_published")
    op.create_index("ix_listings_state", "listings", ["state"])

    # ── Release (listing version) state column ────────────────────────────
    op.add_column(
        "listing_versions",
        sa.Column("state", sa.String(30), nullable=False, server_default="draft"),
    )
    op.create_index("ix_listing_versions_state", "listing_versions", ["state"])

    # ── Creator state column on users ─────────────────────────────────────
    op.add_column(
        "users",
        sa.Column(
            "creator_state",
            sa.String(30),
            nullable=False,
            server_default="pending_approval",
        ),
    )
    # Existing verified users become approved creators
    op.execute("UPDATE users SET creator_state = 'approved' WHERE is_verified = true")

    # ── Listing moderation events ─────────────────────────────────────────
    op.create_table(
        "listing_moderation_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("from_state", sa.String(30), nullable=False),
        sa.Column("to_state", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_listing_moderation_events_listing_id",
        "listing_moderation_events",
        ["listing_id"],
    )

    # ── Creator moderation events ─────────────────────────────────────────
    op.create_table(
        "creator_moderation_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "creator_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("from_state", sa.String(30), nullable=False),
        sa.Column("to_state", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_creator_moderation_events_creator_id",
        "creator_moderation_events",
        ["creator_id"],
    )

    # ── Release moderation events ─────────────────────────────────────────
    op.create_table(
        "release_moderation_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "release_id",
            UUID(as_uuid=True),
            sa.ForeignKey("listing_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "listing_id",
            UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("from_state", sa.String(30), nullable=False),
        sa.Column("to_state", sa.String(30), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_release_moderation_events_release_id",
        "release_moderation_events",
        ["release_id"],
    )
    op.create_index(
        "ix_release_moderation_events_listing_id",
        "release_moderation_events",
        ["listing_id"],
    )

    # ── Reports ───────────────────────────────────────────────────────────
    op.create_table(
        "reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reporter_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolution_note", sa.Text, nullable=True),
        sa.Column(
            "resolved_by_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_reports_reporter_id", "reports", ["reporter_id"])
    op.create_index("ix_reports_entity_id", "reports", ["entity_id"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("release_moderation_events")
    op.drop_table("creator_moderation_events")
    op.drop_table("listing_moderation_events")

    op.drop_column("users", "creator_state")

    op.drop_index("ix_listing_versions_state", table_name="listing_versions")
    op.drop_column("listing_versions", "state")

    op.drop_index("ix_listings_state", table_name="listings")
    op.add_column(
        "listings",
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
    )
    op.execute("UPDATE listings SET is_published = true WHERE state = 'published'")
    op.drop_column("listings", "state")
