from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class RecognitionScore(Base):
    """Automated recognition points. Fair and objective, based on quantifiable actions."""

    __tablename__ = "recognition_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    points = Column(Float, default=0)
    period_start = Column(DateTime(timezone=True), nullable=False)  # Week start
    period_end = Column(DateTime(timezone=True), nullable=False)  # Week end
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="recognition_scores")
