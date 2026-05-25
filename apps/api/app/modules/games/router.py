from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.games.schemas import GameResponse
from app.modules.games.service import list_games, search_games

router = APIRouter(prefix="/games", tags=["games"])


@router.get("")
async def get_games(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_games(db, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/search")
async def search(
    q: str | None = Query(None),
    home_q: str | None = Query(None),
    away_q: str | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    items = await search_games(db, q, home_q, away_q, limit)
    return items
