from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class MeetingPoll(Base):
    """A poll for scheduling the next team meeting. Contains 30-min slots for a week."""

    __tablename__ = "meeting_polls"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    title = Column(String(255), nullable=False)
    week_start = Column(DateTime(timezone=True), nullable=False)  # Start of voting week
    week_end = Column(DateTime(timezone=True), nullable=False)  # End of voting week
    winning_slot_start = Column(DateTime(timezone=True), nullable=True)  # Selected slot
    google_event_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    is_scheduled = Column(Boolean, default=False)

    slot_votes = relationship("MeetingSlotVote", back_populates="meeting_poll", cascade="all, delete-orphan")


class MeetingSlotVote(Base):
    """A user's vote for a specific 30-minute slot in a meeting poll."""

    __tablename__ = "meeting_slot_votes"

    id = Column(Integer, primary_key=True, index=True)
    meeting_poll_id = Column(Integer, ForeignKey("meeting_polls.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_start = Column(DateTime(timezone=True), nullable=False)
    slot_end = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    meeting_poll = relationship("MeetingPoll", back_populates="slot_votes")
    user = relationship("User", back_populates="slot_votes")
