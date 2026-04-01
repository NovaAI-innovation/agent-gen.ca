from sqlalchemy import Boolean, Column, Integer, String, DateTime

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

import app.db.database as db


class User(db.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(42), unique=True, index=True, nullable=False)  # Ethereum address
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Agents owned by this user
    agents = relationship("Agent", back_populates="owner")
