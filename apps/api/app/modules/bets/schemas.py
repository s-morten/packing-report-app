from datetime import datetime

from pydantic import BaseModel, field_validator


class PlaceBetRequest(BaseModel):
    home_team: str
    away_team: str
    stake: float
    odds: float
    placed_at: datetime | None = None

    @field_validator("stake", "odds")
    @classmethod
    def positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Must be positive")
        return v


class UpdateBetRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        if v not in ("won", "lost", "void"):
            raise ValueError("Status must be won, lost, or void")
        return v


class BetResponse(BaseModel):
    id: int
    user_id: int
    home_team: str
    away_team: str
    stake: float
    odds: float
    status: str
    placed_at: datetime
    settled_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PaginatedBetsResponse(BaseModel):
    items: list[BetResponse]
    total: int
    offset: int
    limit: int
