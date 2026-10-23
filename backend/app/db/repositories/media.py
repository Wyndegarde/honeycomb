from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Media, MediaType
from app.db.repositories.base import AsyncBaseRepository


class MediaRepository(AsyncBaseRepository[Media]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Media, db)

    async def search(
        self,
        q: str | None = None,
        media_type: MediaType | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> Sequence[Media]:
        stmt = select(Media).order_by(Media.id).offset(offset)
        if q:
            # Escape LIKE wildcards so "100%" or "a_b" match literally
            escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            stmt = stmt.where(
                or_(
                    Media.title.ilike(pattern, escape="\\"),
                    Media.creator.ilike(pattern, escape="\\"),
                )
            )
        if media_type:
            stmt = stmt.where(Media.media_type == media_type)
        if limit is not None:
            stmt = stmt.limit(limit)
        return (await self.db.scalars(stmt)).all()
