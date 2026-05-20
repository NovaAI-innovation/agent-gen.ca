import uuid
import app.db.database as db
from sqlalchemy import Boolean, Column, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


class AuthNonce(db.Base):
    __tablename__ = "auth_nonces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_address = Column(String(44), nullable=False)
    nonce = Column(String(64), nullable=False, unique=True)
    message = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    uri = Column(Text, nullable=False)
    chain_id = Column(String(64), nullable=False)
    issued_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
