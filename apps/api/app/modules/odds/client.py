import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

BASE_URL = settings.odds_api_base_url.rstrip("/")
TIMEOUT = 30.0


class OddsAPIClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._api_key = settings.odds_api_key

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=TIMEOUT)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> list | dict:
        if not self._client:
            raise RuntimeError("Client not initialized — use async context manager")
        params = {**(params or {}), "apiKey": self._api_key}
        url = f"{BASE_URL}{path}"
        logger.info("odds_api_request", url=url, params=params)
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def fetch_sports(self) -> list[dict]:
        return await self._get("/sports")

    async def fetch_odds(
        self, sport_key: str, regions: str = "eu", markets: str = "h2h"
    ) -> list[dict]:
        return await self._get(
            f"/sports/{sport_key}/odds",
            params={"regions": regions, "markets": markets},
        )


LEAGUE_SPORT_MAP: dict[str, str] = {
    "Bundesliga": "soccer_germany_bundesliga",
    "2. Bundesliga": "soccer_germany_2_bundesliga",
    "3. Liga": "soccer_germany_3_liga",
}
