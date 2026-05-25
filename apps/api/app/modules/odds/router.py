from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Bookmaker, Event, League, MarketOutcome, OddsSnapshot, Team
from app.modules.odds.schemas import (
    BookmakerOdds,
    EventResponse,
    LeagueResponse,
    OddsResponse,
    OutcomeOdds,
    TeamResponse,
)

router = APIRouter(tags=["odds"])


@router.get("/teams")
async def get_teams(q: str | None = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Team).order_by(Team.name)
    if q:
        query = query.where(Team.name.ilike(f"%{q}%"))
    result = await db.execute(query)
    return [{"id": t.id, "name": t.name} for t in result.scalars().all()]


@router.get("/leagues")
async def get_leagues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(League).order_by(League.name))
    return [LeagueResponse.model_validate(l) for l in result.scalars().all()]


@router.get("/events")
async def get_events(league_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.home_team), selectinload(Event.away_team))
        .where(Event.league_id == league_id)
        .order_by(Event.start_time)
    )
    return [EventResponse.model_validate(e) for e in result.scalars().all()]


@router.get("/odds")
async def get_odds(event_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    event_result = await db.execute(
        select(Event)
        .options(selectinload(Event.home_team), selectinload(Event.away_team))
        .where(Event.id == event_id)
    )
    event = event_result.scalar_one_or_none()
    if not event:
        return {"error": "Event not found"}

    result = await db.execute(
        select(OddsSnapshot, Bookmaker.name, MarketOutcome.name, MarketOutcome.id)
        .join(Bookmaker, OddsSnapshot.bookmaker_id == Bookmaker.id)
        .join(MarketOutcome, OddsSnapshot.market_outcome_id == MarketOutcome.id)
        .where(OddsSnapshot.event_id == event_id)
    )
    rows = result.all()

    bookmaker_map: dict[int, dict] = {}
    for snapshot, bm_name, outcome_name, outcome_id in rows:
        bm_id = snapshot.bookmaker_id
        if bm_id not in bookmaker_map:
            bookmaker_map[bm_id] = {
                "bookmaker_id": bm_id,
                "bookmaker_name": bm_name,
                "outcomes": [],
            }
        key = outcome_name.lower()
        bookmaker_map[bm_id][key] = snapshot.odds
        bookmaker_map[bm_id]["outcomes"].append(
            OutcomeOdds(market_outcome_id=outcome_id, name=outcome_name, odds=snapshot.odds)
        )

    bookmaker_odds = [
        BookmakerOdds(**v) for v in bookmaker_map.values()
    ]

    return OddsResponse(
        event=EventResponse.model_validate(event),
        bookmaker_odds=bookmaker_odds,
    ).model_dump()
