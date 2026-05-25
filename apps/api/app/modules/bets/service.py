from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, UnauthorizedException
from app.models import Bet
from app.modules.bets.schemas import BetResponse


async def place_bet(
    db: AsyncSession,
    user_id: int,
    home_team: str,
    away_team: str,
    stake: float,
    odds: float,
    placed_at: datetime | None = None,
) -> Bet:
    bet = Bet(
        user_id=user_id,
        home_team=home_team,
        away_team=away_team,
        stake=stake,
        odds=odds,
        status="open",
        placed_at=placed_at or datetime.now(timezone.utc),
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
