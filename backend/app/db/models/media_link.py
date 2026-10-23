from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseNoDate


class MediaLink(Base):
    """Undirected edge between two media. Stored with source_id < target_id."""

    __table_args__ = (
        CheckConstraint("source_id < target_id", name="ordered_pair"),
        UniqueConstraint("source_id", "target_id", name="uq_media_link_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[int] = mapped_column(
        ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class MediaLinkTheme(BaseNoDate):
    link_id: Mapped[int] = mapped_column(
        ForeignKey("media_link.id", ondelete="CASCADE"), primary_key=True
    )
    theme_id: Mapped[int] = mapped_column(
        ForeignKey("theme.id", ondelete="CASCADE"), primary_key=True, index=True
    )
