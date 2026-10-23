from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Review
from app.db.repositories.base import AsyncBaseRepository


class ReviewRepository(AsyncBaseRepository[Review]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Review, db)

    async def get_by_media_id(self, media_id: int) -> Review | None:
        return await self.get_by_field("media_id", media_id)

    async def upsert(self, media_id: int, rating: int, body: str | None) -> Review:
        """Create or replace the review for a media item in one statement, so
        two concurrent calls cannot both try to insert."""
        stmt = (
            insert(Review)
            .values(media_id=media_id, rating=rating, body=body)
            .on_conflict_do_update(
                index_elements=[Review.media_id],
                set_={"rating": rating, "body": body, "updated_at": func.now()},
            )
            .returning(Review)
            .execution_options(populate_existing=True)
        )
        return (await self.db.scalars(stmt)).one()
