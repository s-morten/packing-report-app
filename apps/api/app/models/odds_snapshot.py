from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class OddsSnapshot(Base):
    __tablename__ = "odds_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    bookmaker_id: Mapped[int] = mapped_column(
        ForeignKey("bookmaker.id"), nullable=False
    )
    market_outcome_id: Mapped[int] = mapped_column(
        ForeignKey("market_outcome.id"), nullable=False
    )
    odds: Mapped[float] = mapped_column(Float, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    event: Mapped["Event"] = relationship(back_populates="odds_snapshots")
    bookmaker: Mapped["Bookmaker"] = relationship(back_populates="odds_snapshots")
    market_outcome: Mapped["MarketOutcome"] = relationship(
        back_populates="odds_snapshots"
    )
