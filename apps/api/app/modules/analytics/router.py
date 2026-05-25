from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.analytics.schemas import StatsResponse
from app.modules.analytics.service import compute_stats

router = APIRouter(prefix="/stats", tags=["analytics"])


@router.get("", response_model=StatsResponse)
async def get_stats(
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    from_dt = (
        datetime.fromisoformat(from_date.replace("Z", "+00:00"))
        if from_date
        else None
    )
    to_dt = (
        datetime.fromisoformat(to_date.replace("Z", "+00:00")) if to_date else None
    )

    stats = await compute_stats(db, user_id, from_dt, to_dt)
    return StatsResponse(**stats)
