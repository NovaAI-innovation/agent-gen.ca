"""Add web3 payment foundation tables and auth nonce SIWS fields

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    payment_intent_status = postgresql.ENUM(
        "pending",
        "submitted",
        "confirmed",
        "failed",
        "expired",
        name="payment_intent_status",
    )
    payment_intent_status.create(op.get_bind())

    # Structured SIWS challenge persistence
    op.add_column("auth_nonces", sa.Column("message", sa.Text(), nullable=True))
    op.add_column("auth_nonces", sa.Column("domain", sa.String(length=255), nullable=True))
    op.add_column("auth_nonces", sa.Column("uri", sa.Text(), nullable=True))
    op.add_column("auth_nonces", sa.Column("chain_id", sa.String(length=64), nullable=True))
    op.add_column(
        "auth_nonces",
        sa.Column("issued_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=True),
    )

    op.execute("UPDATE auth_nonces SET message = '' WHERE message IS NULL")
    op.execute("UPDATE auth_nonces SET domain = 'agent-gen.ca' WHERE domain IS NULL")
    op.execute("UPDATE auth_nonces SET uri = 'https://agent-gen.ca' WHERE uri IS NULL")
    op.execute("UPDATE auth_nonces SET chain_id = 'solana:mainnet' WHERE chain_id IS NULL")
    op.execute("UPDATE auth_nonces SET issued_at = NOW() WHERE issued_at IS NULL")

    op.alter_column("auth_nonces", "message", nullable=False)
    op.alter_column("auth_nonces", "domain", nullable=False)
    op.alter_column("auth_nonces", "uri", nullable=False)
    op.alter_column("auth_nonces", "chain_id", nullable=False)
    op.alter_column("auth_nonces", "issued_at", nullable=False)

    # Purchases become chain-aware
    op.add_column(
        "purchases",
        sa.Column(
            "currency_mint",
            sa.String(length=44),
            server_default="So11111111111111111111111111111111111111112",
            nullable=False,
        ),
    )
    op.add_column("purchases", sa.Column("amount_lamports", sa.BigInteger(), nullable=True))
    op.add_column(
        "purchases",
        sa.Column("cluster", sa.String(length=32), server_default="mainnet-beta", nullable=False),
    )
    op.add_column("purchases", sa.Column("confirmed_slot", sa.BigInteger(), nullable=True))
    op.add_column("purchases", sa.Column("finalized_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("purchases", sa.Column("failure_reason", sa.Text(), nullable=True))

    op.create_index("purchases_cluster_status_idx", "purchases", ["cluster", "status"])

    op.create_table(
        "listing_payment_config",
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("seller_wallet_address", sa.String(length=44), nullable=False),
        sa.Column(
            "accepted_mint",
            sa.String(length=44),
            nullable=False,
            server_default="So11111111111111111111111111111111111111112",
        ),
        sa.Column("platform_fee_bps", sa.Integer(), nullable=False, server_default="250"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "onchain_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("signature", sa.String(length=88), nullable=False),
        sa.Column("cluster", sa.String(length=32), nullable=False),
        sa.Column("slot", sa.BigInteger(), nullable=True),
        sa.Column("confirmation_status", sa.String(length=32), nullable=True),
        sa.Column("err_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("logs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("observed_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("finalized_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint("signature", name="onchain_transactions_signature_unique"),
    )
    op.create_index("onchain_transactions_cluster_slot_idx", "onchain_transactions", ["cluster", "slot"])
    op.create_index(
        "onchain_transactions_cluster_status_idx",
        "onchain_transactions",
        ["cluster", "confirmation_status"],
    )

    op.create_table(
        "payment_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("purchase_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expected_recipient_wallet", sa.String(length=44), nullable=False),
        sa.Column("expected_mint", sa.String(length=44), nullable=False),
        sa.Column("expected_amount_lamports", sa.BigInteger(), nullable=False),
        sa.Column("memo", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("submitted_signature", sa.String(length=88), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "submitted",
                "confirmed",
                "failed",
                "expired",
                name="payment_intent_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("idempotency_key", name="payment_intents_idempotency_key_unique"),
        sa.UniqueConstraint("submitted_signature", name="payment_intents_submitted_signature_unique"),
    )
    op.create_index("payment_intents_status_expires_idx", "payment_intents", ["status", "expires_at"])
    op.create_index("payment_intents_listing_buyer_idx", "payment_intents", ["listing_id", "buyer_id"])

    op.create_table(
        "entitlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listing_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("purchase_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="purchase"),
        sa.Column("granted_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("entitlements_user_listing_idx", "entitlements", ["user_id", "listing_id"])
    op.create_index("entitlements_purchase_idx", "entitlements", ["purchase_id"])


def downgrade() -> None:
    op.drop_index("entitlements_purchase_idx", table_name="entitlements")
    op.drop_index("entitlements_user_listing_idx", table_name="entitlements")
    op.drop_table("entitlements")

    op.drop_index("payment_intents_listing_buyer_idx", table_name="payment_intents")
    op.drop_index("payment_intents_status_expires_idx", table_name="payment_intents")
    op.drop_table("payment_intents")

    op.drop_index("onchain_transactions_cluster_status_idx", table_name="onchain_transactions")
    op.drop_index("onchain_transactions_cluster_slot_idx", table_name="onchain_transactions")
    op.drop_table("onchain_transactions")

    op.drop_table("listing_payment_config")

    op.drop_index("purchases_cluster_status_idx", table_name="purchases")
    op.drop_column("purchases", "failure_reason")
    op.drop_column("purchases", "finalized_at")
    op.drop_column("purchases", "confirmed_slot")
    op.drop_column("purchases", "cluster")
    op.drop_column("purchases", "amount_lamports")
    op.drop_column("purchases", "currency_mint")

    op.drop_column("auth_nonces", "issued_at")
    op.drop_column("auth_nonces", "chain_id")
    op.drop_column("auth_nonces", "uri")
    op.drop_column("auth_nonces", "domain")
    op.drop_column("auth_nonces", "message")

    op.execute("DROP TYPE IF EXISTS payment_intent_status")
