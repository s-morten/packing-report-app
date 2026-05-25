from datetime import datetime

from pydantic import BaseModel


class GameResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    date: datetime
    goals_home: int
    goals_away: int

    model_config = {"from_attributes": True}
