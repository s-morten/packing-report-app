from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MarketOutcome(Base, TimestampMixin):
    __tablename__ = "market_outcome"

    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("market.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100))

    market: Mapped["Market"] = relationship(back_populates="outcomes")
    odds_snapshots: Mapped[list["OddsSnapshot"]] = relationship(
        back_populates="market_outcome"
    )
