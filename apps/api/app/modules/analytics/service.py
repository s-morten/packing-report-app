from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet


async def compute_stats(
    db: AsyncSession,
    user_id: int,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> dict:
    base = select(Bet).where(Bet.user_id == user_id)
    if from_date:
        base = base.where(Bet.placed_at >= from_date)
    if to_date:
        base = base.where(Bet.placed_at <= to_date)

    result = await db.execute(base)
    all_bets = result.scalars().all()

    total_bets = len(all_bets)
    won = sum(1 for b in all_bets if b.status == "won")
    lost = sum(1 for b in all_bets if b.status == "lost")
    void = sum(1 for b in all_bets if b.status == "void")

    total_stake = sum(b.stake for b in all_bets)
    total_profit = sum(
        b.stake * b.odds - b.stake if b.status == "won" else -b.stake if b.status == "lost" else 0
        for b in all_bets
    )

    roi = (total_profit / total_stake * 100) if total_stake > 0 else 0.0
    hit_rate = (won / (won + lost) * 100) if (won + lost) > 0 else 0.0

    sorted_bets = sorted(all_bets, key=lambda b: b.placed_at)
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    time_series_map: dict[str, dict[str, float]] = {}

    for b in sorted_bets:
        day = b.placed_at.strftime("%Y-%m-%d")
        profit = (
            b.stake * b.odds - b.stake
            if b.status == "won"
            else -b.stake if b.status == "lost" else 0
        )
        stake = b.stake if b.status in ("won", "lost") else 0

        if day not in time_series_map:
            time_series_map[day] = {"profit": 0.0, "stake": 0.0}
        time_series_map[day]["profit"] += profit
        time_series_map[day]["stake"] += stake

    cum_profit = 0.0
    cum_stake = 0.0
    time_series = []
    for day in sorted(time_series_map.keys()):
        cum_profit += time_series_map[day]["profit"]
        cum_stake += time_series_map[day]["stake"]
        time_series.append(
            {"date": day, "cumulative_profit": round(cum_profit, 2), "cumulative_stake": round(cum_stake, 2)}
        )

        if cum_profit > peak:
            peak = cum_profit
        drawdown = peak - cum_profit if peak > 0 else 0.0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return {
        "total_bets": total_bets,
        "won": won,
        "lost": lost,
        "void": void,
        "total_stake": round(total_stake, 2),
        "total_profit": round(total_profit, 2),
        "roi": round(roi, 2),
        "hit_rate": round(hit_rate, 2),
        "max_drawdown": round(max_drawdown, 2),
        "time_series": time_series,
    }
