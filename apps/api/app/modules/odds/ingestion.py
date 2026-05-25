from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Bookmaker,
    Event,
    League,
    Market,
    MarketOutcome,
    OddsSnapshot,
    Sport,
    Team,
)

logger = structlog.get_logger(__name__)
OUTCOME_NAMES = ["Home", "Draw", "Away"]


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def _get_or_create(
    db: AsyncSession, model, commit: bool = False, **filters
) -> tuple:
    result = await db.execute(select(model).filter_by(**filters))
    instance = result.scalar_one_or_none()
    if instance is not None:
        return instance, False
    instance = model(**filters)
    db.add(instance)
    await db.flush()
    if commit:
        await db.commit()
    return instance, True


async def ensure_market_and_outcomes(db: AsyncSession) -> tuple[Market, list[MarketOutcome]]:
    market, _ = await _get_or_create(db, Market, name="h2h", external_id="h2h")
    outcomes = []
    for name in OUTCOME_NAMES:
        outcome, _ = await _get_or_create(
            db, MarketOutcome, market_id=market.id, name=name
        )
        outcomes.append(outcome)
    return market, outcomes


def _map_outcome_name(
    api_name: str, home_team_name: str, away_team_name: str
) -> str:
    if api_name.lower() == "draw":
        return "Draw"
    if api_name == home_team_name:
        return "Home"
    if api_name == away_team_name:
        return "Away"
    return api_name


async def ingest_sport_odds(
    db: AsyncSession,
    league_name: str,
    sport_key: str,
    api_data: list[dict],
) -> dict:
    result = await db.execute(
        select(Sport).where(Sport.slug == sport_key)
    )
    sport = result.scalar_one_or_none()
    if sport is None:
        sport, _ = await _get_or_create(db, Sport, name=league_name, slug=sport_key)

    league_result = await db.execute(
        select(League).where(League.sport_id == sport.id, League.name == league_name)
    )
    league = league_result.scalar_one_or_none()
    if league is None:
        league, _ = await _get_or_create(
            db, League, sport_id=sport.id, name=league_name, country="Germany"
        )

    market, outcomes = await ensure_market_and_outcomes(db)

    stats = {"events": 0, "teams": 0, "bookmakers": 0, "snapshots": 0}

    for event_data in api_data:
        home_name = event_data["home_team"]
        away_name = event_data["away_team"]
        external_id = event_data["id"]
        commence_time = _parse_datetime(event_data["commence_time"])

        home_team, created = await _get_or_create(db, Team, name=home_name)
        if created:
            stats["teams"] += 1

        away_team, created = await _get_or_create(db, Team, name=away_name)
        if created:
            stats["teams"] += 1

        event_result = await db.execute(
            select(Event).where(Event.external_id == external_id)
        )
        event = event_result.scalar_one_or_none()
        if event is None:
            event = Event(
                league_id=league.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                start_time=commence_time,
                status="pending",
                external_id=external_id,
            )
            db.add(event)
            await db.flush()
            stats["events"] += 1
        else:
            event.home_team_id = home_team.id
            event.away_team_id = away_team.id
            event.start_time = commence_time

        for bm_data in event_data.get("bookmakers", []):
            bm_external_id = bm_data["key"]
            bm_name = bm_data["title"]

            bookmaker, created = await _get_or_create(
                db, Bookmaker, external_id=bm_external_id, name=bm_name
            )
            if created:
                stats["bookmakers"] += 1

            for market_data in bm_data.get("markets", []):
                if market_data["key"] != "h2h":
                    continue

                for outcome_data in market_data.get("outcomes", []):
                    mapped_name = _map_outcome_name(
                        outcome_data["name"], home_name, away_name
                    )
                    match_outcome = None
                    for o in outcomes:
                        if o.name == mapped_name:
                            match_outcome = o
                            break
                    if match_outcome is None:
                        continue

                    snapshot = OddsSnapshot(
                        event_id=event.id,
                        bookmaker_id=bookmaker.id,
                        market_outcome_id=match_outcome.id,
                        odds=outcome_data["price"],
                    )
                    db.add(snapshot)
                    stats["snapshots"] += 1

    await db.commit()
    logger.info("ingest_complete", league=league_name, **stats)
    return stats
