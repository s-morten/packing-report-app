import argparse
import asyncio

import structlog
from sqlalchemy import delete

from app.core.config import settings
from app.core.database import async_session
from app.models import OddsSnapshot
from app.modules.odds.client import LEAGUE_SPORT_MAP, OddsAPIClient
from app.modules.odds.ingestion import ingest_sport_odds

logger = structlog.get_logger(__name__)


async def ingest_odds(ctx: dict | None = None) -> dict:
    if not settings.odds_api_key or settings.odds_api_key == "your-odds-api-key-here":
        logger.warning("no_valid_odds_api_key_configured_skipping_ingestion")
        return {"events": 0, "teams": 0, "bookmakers": 0, "snapshots": 0}

    total = {"events": 0, "teams": 0, "bookmakers": 0, "snapshots": 0}

    async with OddsAPIClient() as client:
        for league_name, sport_key in LEAGUE_SPORT_MAP.items():
            logger.info("fetching_odds", league=league_name, sport=sport_key)
            try:
                data = await client.fetch_odds(sport_key)
            except Exception as e:
                logger.error("fetch_failed", league=league_name, error=str(e))
                continue

            if not data:
                logger.info("no_events", league=league_name)
                continue

            async with async_session() as db:
                async with db.begin():
                    await db.execute(delete(OddsSnapshot))
                    await db.flush()

                stats = await ingest_sport_odds(db, league_name, sport_key, data)

            for k, v in stats.items():
                total[k] = total.get(k, 0) + v

    logger.info("ingest_summary", **total)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Odds ingestion CLI")
    parser.add_argument("--ingest", action="store_true", help="Run odds ingestion")
    args = parser.parse_args()

    if args.ingest:
        asyncio.run(ingest_odds())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
