"""Automated recognition scoring based on objective, quantifiable actions."""
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.meeting import MeetingSlotVote
from app.models.recognition import RecognitionScore

# Point allocation (transparent, documented)
POINTS_TASK_COMPLETED = 5
POINTS_PROGRESS_UPDATE = 1  # Per 25% progress increment
POINTS_MEETING_VOTE = 1


async def recalculate_recognition_scores(session: AsyncSession, team_id: int) -> None:
    """
    Recalculate recognition scores for all team members for the current week.
    Fair and automated: based on tasks completed, progress updates, and meeting participation.
    """
    now = datetime.utcnow()
    week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    while week_start.weekday() != 0:  # Monday
        week_start -= timedelta(days=1)
    week_end = week_start + timedelta(days=7)

    # Get all users in team
    from app.models.user import User
    users_result = await session.execute(select(User.id).where(User.team_id == team_id))
    user_ids = [r[0] for r in users_result.scalars().all()]

    for user_id in user_ids:
        points = 0.0

        # Tasks completed this week (status changed to DONE)
        tasks_done = await session.execute(
            select(func.count(Task.id)).where(
                Task.assignee_id == user_id,
                Task.status == TaskStatus.DONE,
                Task.updated_at >= week_start,
                Task.updated_at < week_end,
            )
        )
        points += tasks_done.scalar() * POINTS_TASK_COMPLETED

        # Progress updates (each 25% increment = 1 point, cap at 4 for 0->100)
        tasks_in_progress = await session.execute(
            select(Task).where(
                Task.assignee_id == user_id,
                Task.updated_at >= week_start,
                Task.updated_at < week_end,
            )
        )
        for task in tasks_in_progress.scalars().all():
            prev_progress = 0  # Simplified: assume each update adds points
            progress_steps = task.progress // 25
            points += min(progress_steps * POINTS_PROGRESS_UPDATE, 4)

        # Meeting slot votes this week
        votes_count = await session.execute(
            select(func.count(MeetingSlotVote.id)).where(
                MeetingSlotVote.user_id == user_id,
                MeetingSlotVote.created_at >= week_start,
                MeetingSlotVote.created_at < week_end,
            )
        )
        points += votes_count.scalar() * POINTS_MEETING_VOTE

        # Upsert recognition score
        existing = await session.execute(
            select(RecognitionScore).where(
                RecognitionScore.user_id == user_id,
                RecognitionScore.team_id == team_id,
                RecognitionScore.period_start == week_start,
            )
        )
        rec = existing.scalar_one_or_none()
        if rec:
            rec.points = points
        else:
            rec = RecognitionScore(
                user_id=user_id,
                team_id=team_id,
                points=points,
                period_start=week_start,
                period_end=week_end,
            )
            session.add(rec)

    await session.commit()
