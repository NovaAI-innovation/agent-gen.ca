"""Add creator profile fields to users (handle, display_name, support_link,
terms acceptance, payout address, approval status)

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("handle", sa.String(length=30), nullable=True))
    op.add_column("users", sa.Column("display_name", sa.String(length=60), nullable=True))
    op.add_column("users", sa.Column("support_link", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column("terms_accepted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column("users", sa.Column("payout_address", sa.String(length=44), nullable=True))
    op.add_column(
        "users",
        sa.Column("creator_status", sa.String(length=20), nullable=False, server_default="none"),
    )
    op.add_column(
        "users",
        sa.Column("creator_status_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column("users", sa.Column("reviewer_notes", sa.Text(), nullable=True))

    op.create_unique_constraint("users_handle_unique", "users", ["handle"])
    op.create_index("users_creator_status_idx", "users", ["creator_status"])


def downgrade() -> None:
    op.drop_index("users_creator_status_idx", table_name="users")
    op.drop_constraint("users_handle_unique", "users", type_="unique")
    op.drop_column("users", "reviewer_notes")
    op.drop_column("users", "creator_status_at")
    op.drop_column("users", "creator_status")
    op.drop_column("users", "payout_address")
    op.drop_column("users", "terms_accepted_at")
    op.drop_column("users", "support_link")
    op.drop_column("users", "display_name")
    op.drop_column("users", "handle")