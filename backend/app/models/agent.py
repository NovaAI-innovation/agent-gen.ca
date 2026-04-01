from sqlalchemy

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from sqlalchemy.dialects.postgresql import JSONB

import app.db.database as db

from .user import User


class Agent(db.Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    config_json = Column(JSONB, nullable=False)  # Agent prompt/system/tools config
    price = Column(Float, nullable=False)  # USD price
    image_url = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="agents")
