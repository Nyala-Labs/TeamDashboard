"""User Pydantic schemas."""
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    team_id: int


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
