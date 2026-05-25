from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    date: str
    cumulative_profit: float
    cumulative_stake: float


class StatsResponse(BaseModel):
    total_bets: int
    won: int
    lost: int
    void: int
    total_stake: float
    total_profit: float
    roi: float
    hit_rate: float
    max_drawdown: float
    time_series: list[TimeSeriesPoint]


class TeamStatsItem(BaseModel):
    team: str
    total_bets: int
    won: int
    lost: int
    money_won: float
    money_lost: float


class SelectionStatsItem(BaseModel):
    selection: str
    total_bets: int
    won: int
    lost: int
    money_won: float
    money_lost: float


class OddsBucketItem(BaseModel):
    bucket: str
    total_bets: int
    won: int
    lost: int
    money_won: float
    money_lost: float


class TeamAnalysisResponse(BaseModel):
    by_team: list[TeamStatsItem]
    by_selection: list[SelectionStatsItem]
    by_odds: list[OddsBucketItem]
