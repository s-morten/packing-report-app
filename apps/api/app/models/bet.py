from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Bet(Base, TimestampMixin):
    __tablename__ = "bet"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    bookmaker_id: Mapped[int] = mapped_column(
        ForeignKey("bookmaker.id"), nullable=False
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=False)
    market_outcome_id: Mapped[int] = mapped_column(
        ForeignKey("market_outcome.id"), nullable=False
    )
    stake: Mapped[float] = mapped_column(Float, nullable=False)
    odds: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="bets")
    bookmaker: Mapped["Bookmaker"] = relationship(back_populates="bets")
    event: Mapped["Event"] = relationship(back_populates="bets")
    market_outcome: Mapped["MarketOutcome"] = relationship(back_populates="bets")
