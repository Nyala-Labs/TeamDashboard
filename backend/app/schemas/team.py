"""Team Pydantic schemas."""
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True
