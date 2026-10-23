import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .review import Review


class MediaType(enum.StrEnum):
    BOOK = "book"
    TV_SHOW = "tv_show"
    FILM = "film"
    GAME = "game"
    PODCAST = "podcast"
    OTHER = "other"


class Media(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    creator: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[MediaType] = mapped_column(
        Enum(
            MediaType, name="media_type", values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False,
        index=True,
    )
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    review: Mapped["Review | None"] = relationship(
        back_populates="media",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
