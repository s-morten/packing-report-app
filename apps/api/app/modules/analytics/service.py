from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Bet


_BUCKET_ORDER = {"1-1.5": 0, "1.5-2": 1, "2-5": 2, "5+": 3}


def _bucket_sort_key(bucket: str) -> int:
    return _BUCKET_ORDER.get(bucket, 99)


async def compute_team_analysis(
    db: AsyncSession,
    user_id: int,
) -> dict:
    result = await db.execute(
        select(Bet).where(Bet.user_id == user_id)
    )
    bets = result.scalars().all()

    team_stats: dict[str, dict] = {}
    selection_stats: dict[str, dict] = {
        "home": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
        "draw": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
        "away": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
    }

    odds_buckets: dict[str, dict] = {
        "1-1.5": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
        "1.5-2": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
        "2-5": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
        "5+": {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0},
    }

    def ensure_team(name: str):
        if name not in team_stats:
            team_stats[name] = {"total_bets": 0, "won": 0, "lost": 0, "money_won": 0.0, "money_lost": 0.0}

    for b in bets:
        profit = b.stake * b.odds - b.stake if b.status == "won" else 0.0
        loss = b.stake if b.status == "lost" else 0.0

        sel = selection_stats[b.selection]
        sel["total_bets"] += 1
        if b.status == "won":
            sel["won"] += 1
            sel["money_won"] += profit
        elif b.status == "lost":
            sel["lost"] += 1
            sel["money_lost"] += loss

        bucket = ""
        if b.odds < 1.5:
            bucket = "1-1.5"
        elif b.odds < 2:
            bucket = "1.5-2"
        elif b.odds < 5:
            bucket = "2-5"
        else:
            bucket = "5+"
        bk = odds_buckets[bucket]
        bk["total_bets"] += 1
        if b.status == "won":
            bk["won"] += 1
            bk["money_won"] += profit
        elif b.status == "lost":
            bk["lost"] += 1
            bk["money_lost"] += loss

        for team_name in (b.home_team, b.away_team):
            ensure_team(team_name)
            t = team_stats[team_name]
            t["total_bets"] += 1
            if b.status == "won":
                t["won"] += 1
                t["money_won"] += profit
            elif b.status == "lost":
                t["lost"] += 1
                t["money_lost"] += loss

    by_team = sorted(
        team_stats.items(),
        key=lambda x: x[1]["total_bets"],
        reverse=True,
    )
    by_selection = sorted(
        selection_stats.items(),
        key=lambda x: x[1]["total_bets"],
        reverse=True,
    )

    return {
        "by_team": [
            {"team": team, **stats}
            for team, stats in by_team
        ],
        "by_selection": [
            {"selection": sel, **stats}
            for sel, stats in by_selection
        ],
        "by_odds": [
            {"bucket": bucket, **stats}
            for bucket, stats in sorted(odds_buckets.items(), key=lambda x: _bucket_sort_key(x[0]))
        ],
    }


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
