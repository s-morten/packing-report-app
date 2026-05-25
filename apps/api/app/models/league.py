from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class League(Base, TimestampMixin):
    __tablename__ = "league"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sport.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str | None] = mapped_column(String(100))
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    sport: Mapped["Sport"] = relationship(back_populates="leagues")
    events: Mapped[list["Event"]] = relationship(back_populates="league")
