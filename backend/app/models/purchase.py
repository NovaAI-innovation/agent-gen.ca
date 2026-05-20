import uuid
import app.db.database as db
from sqlalchemy import BigInteger, Boolean, Column, Numeric, String, Text, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum


class PurchaseStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"


class Purchase(db.Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    price_sol = Column(Numeric(18, 9), nullable=False)
    currency_mint = Column(String(44), nullable=False, default="So11111111111111111111111111111111111111112")
    amount_lamports = Column(BigInteger, nullable=True)
    tx_signature = Column(String(88), nullable=True, unique=True)
    status = Column(SAEnum(PurchaseStatus, name="purchase_status"), nullable=False, default=PurchaseStatus.pending)
    cluster = Column(String(32), nullable=False, default="mainnet-beta")
    confirmed_slot = Column(BigInteger, nullable=True)
    finalized_at = Column(TIMESTAMP(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    listing = relationship("Listing")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])


class Tip(db.Base):
    __tablename__ = "tips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="SET NULL"), nullable=True)
    amount_sol = Column(Numeric(18, 9), nullable=False)
    tx_signature = Column(String(88), nullable=False, unique=True)
    message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class PaymentIntentStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    confirmed = "confirmed"
    failed = "failed"
    expired = "expired"


class PaymentIntent(db.Base):
    __tablename__ = "payment_intents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    expected_recipient_wallet = Column(String(44), nullable=False)
    expected_mint = Column(String(44), nullable=False)
    expected_amount_lamports = Column(BigInteger, nullable=False)
    memo = Column(String(128), nullable=True)
    idempotency_key = Column(String(64), nullable=False, unique=True)
    submitted_signature = Column(String(88), nullable=True, unique=True)
    status = Column(
        SAEnum(PaymentIntentStatus, name="payment_intent_status"),
        nullable=False,
        default=PaymentIntentStatus.pending,
    )
    failure_reason = Column(Text, nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OnchainTransaction(db.Base):
    __tablename__ = "onchain_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signature = Column(String(88), nullable=False, unique=True)
    cluster = Column(String(32), nullable=False)
    slot = Column(BigInteger, nullable=True)
    confirmation_status = Column(String(32), nullable=True)
    err_json = Column(JSONB, nullable=True)
    logs_json = Column(JSONB, nullable=True)
    raw_meta_json = Column(JSONB, nullable=True)
    observed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    finalized_at = Column(TIMESTAMP(timezone=True), nullable=True)


class ListingPaymentConfig(db.Base):
    __tablename__ = "listing_payment_config"

    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True)
    seller_wallet_address = Column(String(44), nullable=False)
    accepted_mint = Column(String(44), nullable=False, default="So11111111111111111111111111111111111111112")
    platform_fee_bps = Column(BigInteger, nullable=False, default=250)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Entitlement(db.Base):
    __tablename__ = "entitlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("listing_versions.id", ondelete="SET NULL"), nullable=True)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(32), nullable=False, default="purchase")
    granted_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
