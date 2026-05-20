"""Add index on auth_nonces.expires_at for efficient nonce cleanup

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-04
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_auth_nonces_expires_at",
        "auth_nonces",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_nonces_expires_at", table_name="auth_nonces")
