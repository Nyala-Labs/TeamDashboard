"""Events API router."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Event
from app.schemas.event import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    session: AsyncSession = Depends(get_session),
    team_id: int | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
):
    """List upcoming events, optionally filtered by team and date range."""
    q = select(Event)
    if team_id:
        q = q.where(Event.team_id == team_id)
    if from_date:
        q = q.where(Event.start_time >= from_date)
    if to_date:
        q = q.where(Event.end_time <= to_date)
    q = q.order_by(Event.start_time.asc())
    result = await session.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    payload: EventCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new event."""
    event = Event(**payload.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single event by ID."""
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    payload: EventUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an event."""
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(event, k, v)
    await session.commit()
    await session.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Delete an event."""
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await session.delete(event)
    await session.commit()
