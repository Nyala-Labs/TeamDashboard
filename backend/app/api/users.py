"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import User
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    team_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List users, optionally filtered by team."""
    q = select(User)
    if team_id:
        q = q.where(User.team_id == team_id)
    q = q.order_by(User.name)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user by ID."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a new user."""
    user = User(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
