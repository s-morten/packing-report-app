from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.id"), nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="pending")
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    league: Mapped["League"] = relationship(back_populates="events")
    home_team: Mapped["Team"] = relationship(
        foreign_keys=[home_team_id], back_populates="home_events"
    )
    away_team: Mapped["Team"] = relationship(
        foreign_keys=[away_team_id], back_populates="away_events"
    )
    odds_snapshots: Mapped[list["OddsSnapshot"]] = relationship(back_populates="event")
    bets: Mapped[list["Bet"]] = relationship(back_populates="event")
