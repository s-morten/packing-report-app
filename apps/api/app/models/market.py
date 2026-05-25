from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Market(Base, TimestampMixin):
    __tablename__ = "market"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    outcomes: Mapped[list["MarketOutcome"]] = relationship(back_populates="market")
