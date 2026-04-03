"""Add stateful auth sessions and auth audit events

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wallet_address", sa.String(44), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("refresh_token_hash", name="auth_sessions_refresh_token_hash_unique"),
    )
    op.create_index("auth_sessions_user_status_idx", "auth_sessions", ["user_id", "status"])
    op.create_index("auth_sessions_wallet_idx", "auth_sessions", ["wallet_address"])
    op.create_index("auth_sessions_expires_idx", "auth_sessions", ["expires_at"])
    op.create_index("auth_sessions_revoked_idx", "auth_sessions", ["revoked_at"])

    op.create_table(
        "auth_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("auth_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("wallet_address", sa.String(44), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_agent_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("auth_audit_events_user_idx", "auth_audit_events", ["user_id"])
    op.create_index("auth_audit_events_session_idx", "auth_audit_events", ["session_id"])
    op.create_index("auth_audit_events_wallet_idx", "auth_audit_events", ["wallet_address"])
    op.create_index("auth_audit_events_event_type_idx", "auth_audit_events", ["event_type"])
    op.create_index("auth_audit_events_created_at_idx", "auth_audit_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("auth_audit_events")
    op.drop_table("auth_sessions")
