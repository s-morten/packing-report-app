import asyncio

import structlog
from arq import cron
from arq.connections import RedisSettings
from arq.worker import create_worker

from app.core.config import settings
from app.modules.odds.tasks import ingest_odds

logger = structlog.get_logger(__name__)

redis_settings = RedisSettings.from_dsn(settings.redis_url)


class WorkerSettings:
    redis_settings = redis_settings
    functions = [ingest_odds]
    keep_result = 0
    keep_result_duration = 60
    poll_delay = 3
    cron_jobs = [
        cron(ingest_odds, minute={0, 15, 30, 45}),
    ]


async def main():
    logger.info("starting_arq_worker")
    worker = create_worker(WorkerSettings)
    await worker.async_run()


if __name__ == "__main__":
    asyncio.run(main())
