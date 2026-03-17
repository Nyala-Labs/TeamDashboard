"""Meeting poll API: create poll, vote on slots, compute winner, schedule via Google Calendar."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import MeetingPoll, MeetingSlotVote, Team, User
from app.schemas.meeting import (
    MeetingPollCreate,
    MeetingPollResponse,
    SlotVoteCreate,
    SlotVoteResponse,
    SlotWithVotes,
)
from app.services.google_calendar import create_calendar_event

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _get_winning_slot(slots_with_votes: list[tuple]) -> tuple | None:
    """Return winning slot: highest votes, earliest time on tie."""
    if not slots_with_votes:
        return None
    return sorted(
        slots_with_votes,
        key=lambda x: (-x[2], x[0]),  # -votes desc, slot_start asc
    )[0]


@router.get("/polls", response_model=list[MeetingPollResponse])
async def list_polls(
    team_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List meeting polls, optionally filtered by team."""
    q = select(MeetingPoll)
    if team_id:
        q = q.where(MeetingPoll.team_id == team_id)
    q = q.order_by(MeetingPoll.created_at.desc())
    result = await session.execute(q)
    return list(result.scalars().all())


@router.post("/polls", response_model=MeetingPollResponse, status_code=201)
async def create_poll(
    payload: MeetingPollCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new meeting poll for a week of 30-min slots."""
    poll = MeetingPoll(**payload.model_dump())
    session.add(poll)
    await session.commit()
    await session.refresh(poll)
    return poll


@router.get("/polls/{poll_id}", response_model=MeetingPollResponse)
async def get_poll(
    poll_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a poll by ID."""
    result = await session.execute(select(MeetingPoll).where(MeetingPoll.id == poll_id))
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll


def _generate_week_slots(week_start: datetime, week_end: datetime) -> list[tuple[datetime, datetime]]:
    """Generate all 30-minute intervals between week_start and week_end."""
    slots = []
    current = week_start
    while current < week_end:
        slot_end = current + timedelta(minutes=30)
        if slot_end <= week_end:
            slots.append((current, slot_end))
        current = slot_end
    return slots


@router.get("/polls/{poll_id}/slots", response_model=list[SlotWithVotes])
async def get_poll_slots_with_votes(
    poll_id: int,
    all_slots: bool = Query(True, description="Include all 30-min slots (with 0 votes if none)"),
    session: AsyncSession = Depends(get_session),
):
    """List all 30-min slots in the poll week with vote counts."""
    result = await session.execute(select(MeetingPoll).where(MeetingPoll.id == poll_id))
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")

    vote_map: dict[tuple, int] = {}
    q = (
        select(
            MeetingSlotVote.slot_start,
            MeetingSlotVote.slot_end,
            func.count(MeetingSlotVote.id).label("votes"),
        )
        .where(MeetingSlotVote.meeting_poll_id == poll_id)
        .group_by(MeetingSlotVote.slot_start, MeetingSlotVote.slot_end)
    )
    rows = (await session.execute(q)).all()
    for r in rows:
        vote_map[(r[0], r[1])] = r[2]

    if all_slots:
        slots = _generate_week_slots(poll.week_start, poll.week_end)
        return [
            SlotWithVotes(slot_start=s[0], slot_end=s[1], votes=vote_map.get((s[0], s[1]), 0))
            for s in slots
        ]
    return [SlotWithVotes(slot_start=r[0], slot_end=r[1], votes=r[2]) for r in rows]


@router.post("/votes", response_model=SlotVoteResponse, status_code=201)
async def cast_vote(
    payload: SlotVoteCreate,
    session: AsyncSession = Depends(get_session),
):
    """Vote for a 30-min slot. Re-voting replaces previous vote for that poll."""
    # Ensure poll exists
    result = await session.execute(
        select(MeetingPoll).where(MeetingPoll.id == payload.meeting_poll_id)
    )
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll.is_scheduled:
        raise HTTPException(status_code=400, detail="Poll is closed, meeting already scheduled")

    # Delete existing vote from this user for this poll (allow re-voting)
    await session.execute(
        select(MeetingSlotVote).where(
            MeetingSlotVote.meeting_poll_id == payload.meeting_poll_id,
            MeetingSlotVote.user_id == payload.user_id,
        )
    )
    existing = (await session.execute(
        select(MeetingSlotVote).where(
            MeetingSlotVote.meeting_poll_id == payload.meeting_poll_id,
            MeetingSlotVote.user_id == payload.user_id,
        )
    )).scalars().all()
    for v in existing:
        await session.delete(v)

    vote = MeetingSlotVote(**payload.model_dump())
    session.add(vote)
    await session.commit()
    await session.refresh(vote)
    return vote


@router.post("/polls/{poll_id}/finalize")
async def finalize_poll(
    poll_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Compute winning slot (highest votes, earliest on tie), schedule on Google Calendar.
    """
    result = await session.execute(select(MeetingPoll).where(MeetingPoll.id == poll_id))
    poll = result.scalar_one_or_none()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll.is_scheduled:
        raise HTTPException(status_code=400, detail="Meeting already scheduled")

    # Aggregate votes per slot
    q = (
        select(
            MeetingSlotVote.slot_start,
            MeetingSlotVote.slot_end,
            func.count(MeetingSlotVote.id).label("votes"),
        )
        .where(MeetingSlotVote.meeting_poll_id == poll_id)
        .group_by(MeetingSlotVote.slot_start, MeetingSlotVote.slot_end)
    )
    rows = (await session.execute(q)).all()
    winning = _get_winning_slot(rows) if rows else None

    if not winning:
        raise HTTPException(
            status_code=400,
            detail="No votes cast. Cannot schedule meeting.",
        )

    slot_start, slot_end, _ = winning
    poll.winning_slot_start = slot_start
    poll.is_scheduled = True

    # Schedule on Google Calendar (run sync API in thread pool)
    import asyncio
    try:
        event_id = await asyncio.to_thread(
            create_calendar_event,
            summary=poll.title,
            start_time=slot_start,
            end_time=slot_end,
            description=f"Scheduled from Nyala Labs meeting poll #{poll_id}",
        )
        poll.google_event_id = event_id
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to create Google Calendar event: {e}",
        )

    poll.closed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(poll)
    return {
        "winning_slot_start": slot_start,
        "google_event_id": poll.google_event_id,
    }
