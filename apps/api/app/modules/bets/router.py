from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.bets.schemas import (
    BetResponse,
    PaginatedBetsResponse,
    PlaceBetRequest,
    UpdateBetRequest,
)
from app.modules.bets.service import list_bets, place_bet, update_bet

router = APIRouter(prefix="/bets", tags=["bets"])


@router.post("", response_model=BetResponse, status_code=201)
async def create_bet(
    payload: PlaceBetRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bet = await place_bet(
        db,
        user_id,
        payload.home_team,
        payload.away_team,
        payload.stake,
        payload.odds,
        payload.selection,
        payload.placed_at,
        payload.game_id,
    )
    return bet


@router.get("", response_model=PaginatedBetsResponse)
async def get_bets(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
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

    items, total = await list_bets(db, user_id, offset, limit, from_dt, to_dt)
    return PaginatedBetsResponse(items=items, total=total, offset=offset, limit=limit)


@router.patch("/{bet_id}", response_model=BetResponse)
async def patch_bet(
    bet_id: int,
    payload: UpdateBetRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    bet = await update_bet(db, bet_id, user_id, payload.status)
    return bet
