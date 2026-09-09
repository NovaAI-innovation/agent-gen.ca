"""Add rotation_counter to auth_sessions and composite unique constraint on auth_nonces

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add rotation_counter for optimistic locking during concurrent refresh
    op.add_column(
        "auth_sessions",
        sa.Column("rotation_counter", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )

    # Drop the old unique constraint on nonce alone
    op.drop_constraint("auth_nonces_nonce_unique", "auth_nonces", type_="unique")

    # Create composite unique constraint for atomic per-wallet consumption
    op.create_unique_constraint(
        "uq_auth_nonces_nonce_wallet",
        "auth_nonces",
        ["nonce", "wallet_address"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_auth_nonces_nonce_wallet", "auth_nonces", type_="unique")
    op.create_unique_constraint("auth_nonces_nonce_unique", "auth_nonces", ["nonce"])
    op.drop_column("auth_sessions", "rotation_counter")