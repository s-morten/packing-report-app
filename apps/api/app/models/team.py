from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Team(Base, TimestampMixin):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True)

    home_events: Mapped[list["Event"]] = relationship(
        foreign_keys="Event.home_team_id", back_populates="home_team"
    )
    away_events: Mapped[list["Event"]] = relationship(
        foreign_keys="Event.away_team_id", back_populates="away_team"
    )
