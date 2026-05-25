from datetime import datetime

from pydantic import BaseModel


class LeagueResponse(BaseModel):
    id: int
    name: str
    country: str | None

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    id: int
    league_id: int
    home_team: TeamResponse
    away_team: TeamResponse
    start_time: datetime
    status: str

    model_config = {"from_attributes": True}


class BookmakerOdds(BaseModel):
    bookmaker_id: int
    bookmaker_name: str
    home: float
    draw: float
    away: float


class OddsResponse(BaseModel):
    event: EventResponse
    bookmaker_odds: list[BookmakerOdds]
