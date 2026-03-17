"""Meeting poll and slot vote schemas."""
from datetime import datetime
from pydantic import BaseModel


class MeetingPollCreate(BaseModel):
    team_id: int
    title: str
    week_start: datetime
    week_end: datetime


class MeetingPollResponse(BaseModel):
    id: int
    team_id: int
    title: str
    week_start: datetime
    week_end: datetime
    winning_slot_start: datetime | None
    google_event_id: str | None
    is_scheduled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SlotVoteCreate(BaseModel):
    meeting_poll_id: int
    user_id: int
    slot_start: datetime
    slot_end: datetime


class SlotVoteResponse(BaseModel):
    id: int
    meeting_poll_id: int
    user_id: int
    slot_start: datetime
    slot_end: datetime

    class Config:
        from_attributes = True


class SlotWithVotes(BaseModel):
    slot_start: datetime
    slot_end: datetime
    votes: int
