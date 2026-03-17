"""Team API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Team
from app.schemas import TeamCreate, TeamResponse, TeamWithUsers

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamResponse])
async def list_teams(session: AsyncSession = Depends(get_session)):
    """List all teams."""
    result = await session.execute(select(Team).order_by(Team.name))
    return result.scalars().all()


@router.get("/{team_id}", response_model=TeamWithUsers)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    """Get team with users."""
    result = await session.execute(
        select(Team).where(Team.id == team_id).options(selectinload(Team.users))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("", response_model=TeamResponse)
async def create_team(data: TeamCreate, session: AsyncSession = Depends(get_session)):
    """Create a new team."""
    team = Team(**data.model_dump())
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team
