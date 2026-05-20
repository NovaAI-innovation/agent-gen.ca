"""Marketplace schema: replace users/agents with full marketplace tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old tables from 0001
    op.drop_table("agents")
    op.drop_table("users")

    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Enums
    listing_type = postgresql.ENUM(
        "mcp_server", "agent_skill", "custom_agent", "pack",
        name="listing_type",
    )
    listing_type.create(op.get_bind())

    purchase_status = postgresql.ENUM(
        "pending", "confirmed", "failed",
        name="purchase_status",
    )
    purchase_status.create(op.get_bind())

    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("wallet_address", sa.String(44), nullable=False),
        sa.Column("username", sa.String(50), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("reputation_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("wallet_address", name="users_wallet_address_unique"),
    )
    op.create_index("users_wallet_trgm_idx", "users", ["wallet_address"], postgresql_using="gin",
                    postgresql_ops={"wallet_address": "gin_trgm_ops"})

    # auth_nonces
    op.create_table(
        "auth_nonces",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("wallet_address", sa.String(44), nullable=False),
        sa.Column("nonce", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("nonce", name="auth_nonces_nonce_unique"),
    )

    # categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("slug", name="categories_slug_unique"),
    )

    # tags
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.UniqueConstraint("name", name="tags_name_unique"),
    )

    # listings
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column(
            "type",
            postgresql.ENUM(
                "mcp_server",
                "agent_skill",
                "custom_agent",
                "pack",
                name="listing_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("long_description", sa.Text, nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("price_sol", sa.Numeric(18, 9), nullable=False, server_default="0"),
        sa.Column("download_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("view_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("slug", name="listings_slug_unique"),
    )
    op.create_index("listings_title_trgm_idx", "listings", ["title"], postgresql_using="gin",
                    postgresql_ops={"title": "gin_trgm_ops"})

    # listing_versions
    op.create_table(
        "listing_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("changelog", sa.Text, nullable=True),
        sa.Column("config_json", postgresql.JSONB, nullable=True),
        sa.Column("install_instructions", sa.Text, nullable=True),
        sa.Column("is_latest", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("listing_id", "version", name="listing_versions_unique"),
    )

    # listing_categories join
    op.create_table(
        "listing_categories",
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    )

    # listing_tags join
    op.create_table(
        "listing_tags",
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # pack_items
    op.create_table(
        "pack_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("pack_listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("note", sa.Text, nullable=True),
        sa.UniqueConstraint("pack_listing_id", "item_listing_id", name="pack_items_unique"),
    )

    # reviews
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.SmallInteger, nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("is_verified_purchase", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("helpful_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("listing_id", "reviewer_id", name="reviews_unique_per_user"),
    )

    # review_helpful
    op.create_table(
        "review_helpful",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    )

    # user_follows
    op.create_table(
        "user_follows",
        sa.Column("follower_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("following_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # purchases
    op.create_table(
        "purchases",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("price_sol", sa.Numeric(18, 9), nullable=False),
        sa.Column("tx_signature", sa.String(88), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "confirmed",
                "failed",
                name="purchase_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tx_signature", name="purchases_tx_sig_unique"),
    )

    # tips
    op.create_table(
        "tips",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("from_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("amount_sol", sa.Numeric(18, 9), nullable=False),
        sa.Column("tx_signature", sa.String(88), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tx_signature", name="tips_tx_sig_unique"),
    )

    # downloads
    op.create_table(
        "downloads",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listing_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # user_saves
    op.create_table(
        "user_saves",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # install_history
    op.create_table(
        "install_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listing_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installed_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # collections
    op.create_table(
        "collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("curator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_official", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # collection_items
    op.create_table(
        "collection_items",
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
    )

    # Seed categories and tags
    op.execute("""
        INSERT INTO categories (name, slug, description, icon) VALUES
        ('MCP Servers', 'mcp-servers', 'Model Context Protocol server packages', 'server'),
        ('Agent Skills', 'agent-skills', 'Reusable skills and tools for AI agents', 'zap'),
        ('Custom Agents', 'custom-agents', 'Full agent configurations and personalities', 'bot'),
        ('Packs', 'packs', 'Curated bundles of marketplace items', 'package'),
        ('Productivity', 'productivity', 'Productivity and workflow automation', 'briefcase'),
        ('Development', 'development', 'Software development tools and agents', 'code'),
        ('Data & Analytics', 'data-analytics', 'Data processing and analysis', 'bar-chart'),
        ('Security', 'security', 'Security analysis and testing agents', 'shield')
    """)

    op.execute("""
        INSERT INTO tags (name) VALUES
        ('typescript'), ('python'), ('rust'), ('filesystem'), ('database'),
        ('web-search'), ('code-generation'), ('rag'), ('memory'), ('vision'),
        ('free'), ('open-source'), ('official'), ('community'), ('featured')
    """)


def downgrade() -> None:
    for table in [
        "collection_items", "collections", "install_history", "user_saves",
        "downloads", "tips", "purchases", "user_follows", "review_helpful",
        "reviews", "pack_items", "listing_tags", "listing_categories",
        "listing_versions", "listings", "tags", "categories",
        "auth_nonces", "users",
    ]:
        op.drop_table(table)

    op.execute("DROP TYPE IF EXISTS listing_type")
    op.execute("DROP TYPE IF EXISTS purchase_status")
