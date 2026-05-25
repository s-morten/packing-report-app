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
