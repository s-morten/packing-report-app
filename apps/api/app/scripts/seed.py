"""
Seed script to insert historical settled bets for the demo user.

Usage:
    uv run python -m app.scripts.seed
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session
from app.core.security import hash_password
from app.models.bet import Bet
from app.models.user import User

TEAMS = [
    ("Bayern Munich", "Borussia Dortmund"),
    ("Bayer Leverkusen", "RB Leipzig"),
    ("SC Paderborn", "VfL Wolfsburg"),
    ("Eintracht Frankfurt", "Borussia Mönchengladbach"),
    ("VfB Stuttgart", "Werder Bremen"),
    ("Union Berlin", "SC Freiburg"),
    ("Mainz 05", "FC Augsburg"),
    ("TSG Hoffenheim", "1. FC Heidenheim"),
    ("Borussia Dortmund", "Bayern Munich"),
    ("RB Leipzig", "Bayer Leverkusen"),
    ("VfL Wolfsburg", "Eintracht Frankfurt"),
    ("Werder Bremen", "Union Berlin"),
]

OUTCOMES = ["won", "lost", "void"]
OUTCOME_WEIGHTS = [0.4, 0.4, 0.2]

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"


def random_bet(i: int, user_id: int) -> Bet:
    days_ago = random.randint(1, 120)
    placed = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(0, 23))
    home, away = random.choice(TEAMS)
    stake = round(random.uniform(10, 200), 2)
    odds = round(random.uniform(1.2, 6.0), 2)
    status = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS, k=1)[0]
    settled = placed + timedelta(days=random.randint(1, 5)) if status != "open" else None

    return Bet(
        user_id=user_id,
        home_team=home,
        away_team=away,
        stake=stake,
        odds=odds,
        status=status,
        placed_at=placed,
        settled_at=settled,
    )


async def seed(count: int = 50) -> int:
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == DEMO_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
            db.add(user)
            await db.flush()
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        result = await db.execute(select(Bet).where(Bet.user_id == user.id))
        existing = len(result.scalars().all())

        if existing > 0:
            print(f"Demo user already has {existing} bets. Skipping seed to avoid duplicates.")
            return existing

        bets = [random_bet(i, user.id) for i in range(count)]
        for bet in bets:
            db.add(bet)

        await db.commit()
        print(f"Inserted {count} historical bets for {DEMO_EMAIL}")
        return count


def main():
    count = asyncio.run(seed())
    print(f"Done — {count} bets created")


if __name__ == "__main__":
    main()
