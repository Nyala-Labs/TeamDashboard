"""Recognition score schemas."""
from datetime import datetime
from pydantic import BaseModel


class RecognitionScoreResponse(BaseModel):
    id: int
    user_id: int
    team_id: int
    points: float
    period_start: datetime
    period_end: datetime

    class Config:
        from_attributes = True
