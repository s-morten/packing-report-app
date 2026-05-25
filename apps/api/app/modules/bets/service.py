from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, UnauthorizedException
from app.models import Bet, Game
from app.modules.bets.schemas import BetResponse


def _deduce_status(goals_home: int, goals_away: int, selection: str) -> str:
    if goals_home > goals_away:
        return "won" if selection == "home" else "lost"
    if goals_home < goals_away:
        return "won" if selection == "away" else "lost"
    return "won" if selection == "draw" else "lost"


async def place_bet(
    db: AsyncSession,
    user_id: int,
    home_team: str,
    away_team: str,
    stake: float,
    odds: float,
    selection: str = "home",
    placed_at: datetime | None = None,
    game_id: int | None = None,
) -> Bet:
    status = "open"
    settled_at = None

    if game_id is not None:
        result = await db.execute(select(Game).where(Game.id == game_id))
        game = result.scalar_one_or_none()
        if game:
            home_team = game.home_team
            away_team = game.away_team
            if placed_at is None:
                placed_at = game.date
            if game.goals_home is not None and game.goals_away is not None:
                status = _deduce_status(game.goals_home, game.goals_away, selection)
                if status != "open":
                    settled_at = datetime.now(timezone.utc)

    bet = Bet(
        user_id=user_id,
        home_team=home_team,
        away_team=away_team,
        stake=stake,
        odds=odds,
        selection=selection,
        status=status,
        settled_at=settled_at,
        placed_at=placed_at or datetime.now(timezone.utc),
        game_id=game_id,
    )
    db.add(bet)
    await db.commit()
    await db.refresh(bet)
    return bet


async def list_bets(
    db: AsyncSession,
    user_id: int,
    offset: int = 0,
    limit: int = 20,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> tuple[list[BetResponse], int]:
    query = (
        select(Bet)
        .where(Bet.user_id == user_id)
        .order_by(Bet.placed_at.desc())
    )

    count_query = select(func.count(Bet.id)).where(Bet.user_id == user_id)

    if from_date:
        query = query.where(Bet.placed_at >= from_date)
        count_query = count_query.where(Bet.placed_at >= from_date)
    if to_date:
        query = query.where(Bet.placed_at <= to_date)
        count_query = count_query.where(Bet.placed_at <= to_date)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    bets = result.scalars().all()

    items = [BetResponse.model_validate(b) for b in bets]
    return items, total


async def update_bet(
    db: AsyncSession,
    bet_id: int,
    user_id: int,
    status: str,
) -> Bet:
    result = await db.execute(select(Bet).where(Bet.id == bet_id))
    bet = result.scalar_one_or_none()
    if not bet:
        raise NotFoundException("Bet", bet_id)
    if bet.user_id != user_id:
        raise UnauthorizedException("Not authorized to update this bet")

    bet.status = status
    if status != "open":
        bet.settled_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(bet)
    return bet
