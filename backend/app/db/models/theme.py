from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseNoDate


class Theme(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Stored lower-cased and stripped by ThemeRepository so uniqueness is case-insensitive
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class MediaTheme(BaseNoDate):
    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"), primary_key=True
    )
    theme_id: Mapped[int] = mapped_column(
        ForeignKey("theme.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
