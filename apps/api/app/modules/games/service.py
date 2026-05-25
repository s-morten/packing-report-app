import re

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game
from app.modules.games.schemas import GameResponse

SIMILARITY_THRESHOLD = 0.2
_SEPARATORS = re.compile(r"\s+(?:vs?|v\.|–|—|-|@)\s+", re.IGNORECASE)


def _split_query(q: str) -> tuple[str | None, str | None]:
    parts = _SEPARATORS.split(q, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip() or None, parts[1].strip() or None
    return None, None


def _word_filters(column, q: str):
    return [func.similarity(column, word) > SIMILARITY_THRESHOLD for word in q.split()]


async def list_games(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[GameResponse], int]:
    count_q = select(Game)
    total_result = await db.execute(count_q)
    total = len(total_result.scalars().all())

    query = select(Game).order_by(Game.date.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    games = result.scalars().all()

    items = [GameResponse.model_validate(g) for g in games]
    return items, total


async def search_games(
    db: AsyncSession,
    q: str | None = None,
    home_q: str | None = None,
    away_q: str | None = None,
    limit: int = 10,
) -> list[GameResponse]:
    query = select(Game)

    if q and not home_q and not away_q:
        home_q, away_q = _split_query(q)

    if home_q:
        for f in _word_filters(Game.home_team, home_q):
            query = query.where(f)

    if away_q:
        for f in _word_filters(Game.away_team, away_q):
            query = query.where(f)

    if not home_q and not away_q and q:
        words = q.split()
        filters = [
            or_(
                func.similarity(Game.home_team, w) > SIMILARITY_THRESHOLD,
                func.similarity(Game.away_team, w) > SIMILARITY_THRESHOLD,
            )
            for w in words
        ]
        for f in filters:
            query = query.where(f)

    order_cols = []
    if home_q:
        order_cols.append(func.similarity(Game.home_team, home_q).desc())
    if away_q:
        order_cols.append(func.similarity(Game.away_team, away_q).desc())
    order_cols.append(Game.date.desc())
    query = query.order_by(*order_cols).limit(limit)

    result = await db.execute(query)
    games = result.scalars().all()
    return [GameResponse.model_validate(g) for g in games]
