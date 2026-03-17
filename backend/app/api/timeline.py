"""Timeline API - tasks and milestones grouped by team."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

from app.core.database import get_session
from app.models import Task, Event, Team
from pydantic import BaseModel

router = APIRouter(prefix="/timeline", tags=["timeline"])


class TimelineItem(BaseModel):
    id: str
    type: str  # "task" | "event"
    title: str
    start: datetime
    end: datetime | None
    team_id: int
    team_name: str
    status: str | None = None
    progress: int | None = None

    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    teams: dict[int, str]
    items: list[TimelineItem]


@router.get("", response_model=TimelineResponse)
async def get_timeline(
    team_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """Get timeline of tasks and events, grouped by team."""
    # Load teams
    teams_result = await session.execute(select(Team))
    teams = {t.id: t.name for t in teams_result.scalars().all()}

    items: list[TimelineItem] = []

    # Tasks
    q_tasks = select(Task)
    if team_id:
        q_tasks = q_tasks.where(Task.team_id == team_id)
    if from_date:
        q_tasks = q_tasks.where(
            or_(Task.due_date >= from_date, Task.due_date.is_(None))
        )
    if to_date:
        q_tasks = q_tasks.where(
            or_(Task.due_date <= to_date, Task.due_date.is_(None))
        )
    tasks_result = await session.execute(q_tasks)
    for t in tasks_result.scalars().all():
        start = t.due_date or t.created_at
        items.append(
            TimelineItem(
                id=f"task-{t.id}",
                type="task",
                title=t.title,
                start=start,
                end=start,
                team_id=t.team_id,
                team_name=teams.get(t.team_id, "Unknown"),
                status=t.status.value if hasattr(t.status, "value") else str(t.status),
                progress=t.progress,
            )
        )

    # Events
    q_events = select(Event)
    if team_id:
        q_events = q_events.where(Event.team_id == team_id)
    if from_date:
        q_events = q_events.where(Event.start_time >= from_date)
    if to_date:
        q_events = q_events.where(Event.end_time <= to_date)
    events_result = await session.execute(q_events)
    for e in events_result.scalars().all():
        items.append(
            TimelineItem(
                id=f"event-{e.id}",
                type="event",
                title=e.title,
                start=e.start_time,
                end=e.end_time,
                team_id=e.team_id or 0,
                team_name=teams.get(e.team_id, "All") if e.team_id else "All",
            )
        )

    items.sort(key=lambda x: x.start)
    return TimelineResponse(teams=teams, items=items)
