from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)

    team = relationship("Team", back_populates="users")
    tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    slot_votes = relationship("MeetingSlotVote", back_populates="user")
    recognition_scores = relationship("RecognitionScore", back_populates="user")
