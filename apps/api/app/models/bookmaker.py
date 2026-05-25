from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Bookmaker(Base, TimestampMixin):
    __tablename__ = "bookmaker"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    odds_snapshots: Mapped[list["OddsSnapshot"]] = relationship(
        back_populates="bookmaker"
    )
    bets: Mapped[list["Bet"]] = relationship(back_populates="bookmaker")
