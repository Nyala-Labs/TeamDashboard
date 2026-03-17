"""Recognition scores API - automated, fair effort recognition."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import RecognitionScore, Team
from app.schemas.recognition import RecognitionScoreResponse
from app.services.recognition import recalculate_recognition_scores

router = APIRouter(prefix="/recognition", tags=["recognition"])


@router.post("/recalculate")
async def trigger_recalculate(
    team_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Recalculate recognition scores for a team (fair, automated)."""
    r = await session.execute(select(Team).where(Team.id == team_id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Team not found")
    await recalculate_recognition_scores(session, team_id)
    return {"status": "ok", "team_id": team_id}


@router.get("", response_model=list[RecognitionScoreResponse])
async def list_scores(
    team_id: int | None = Query(None),
    user_id: int | None = Query(None),
    session: AsyncSession = Depends(get_session),
):
    """List recognition scores, optionally by team or user."""
    q = select(RecognitionScore)
    if team_id:
        q = q.where(RecognitionScore.team_id == team_id)
    if user_id:
        q = q.where(RecognitionScore.user_id == user_id)
    q = q.order_by(RecognitionScore.period_start.desc())
    result = await session.execute(q)
    return list(result.scalars().all())
