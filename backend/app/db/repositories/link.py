from collections.abc import Sequence

from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MediaLink, MediaLinkTheme, Theme
from app.db.repositories.base import AsyncBaseRepository


class LinkRepository(AsyncBaseRepository[MediaLink]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(MediaLink, db)

    async def get_between(self, a: int, b: int) -> MediaLink | None:
        source, target = sorted((a, b))
        stmt = select(MediaLink).where(
            MediaLink.source_id == source, MediaLink.target_id == target
        )
        return (await self.db.scalars(stmt)).first()

    async def list_for(
        self, media_id: int, limit: int, offset: int
    ) -> Sequence[MediaLink]:
        other = MediaLink.source_id + MediaLink.target_id - media_id
        stmt = (
            select(MediaLink)
            .where(
                or_(MediaLink.source_id == media_id, MediaLink.target_id == media_id)
            )
            .order_by(other)
            .limit(limit)
            .offset(offset)
        )
        return (await self.db.scalars(stmt)).all()

    async def add_link(
        self, a: int, b: int, themes: list[str], note: str | None
    ) -> MediaLink | None:
        """Create the Link, or return None if the pair is already linked."""
        source, target = sorted((a, b))
        stmt = (
            insert(MediaLink)
            .values(source_id=source, target_id=target, note=note)
            .on_conflict_do_nothing(index_elements=["source_id", "target_id"])
            .returning(MediaLink.id)
        )
        link_id = (await self.db.scalars(stmt)).first()
        if link_id is None:
            return None
        await self._set_themes(link_id, themes)
        return await self._reload(link_id)

    async def update_link(
        self,
        link: MediaLink,
        themes: list[str] | None,
        note: str | None,
        set_note: bool,
    ) -> MediaLink:
        if themes is not None:
            await self._set_themes(link.id, themes)
        if set_note:
            link.note = note
        await self.db.flush()
        return await self._reload(link.id)

    async def _set_themes(self, link_id: int, names: list[str]) -> None:
        # Sorted so concurrent requests take row locks in the same order
        stmt = (
            insert(Theme)
            .values([{"name": n} for n in sorted(names)])
            .on_conflict_do_nothing(index_elements=[Theme.name])
        )
        await self.db.execute(stmt)
        theme_ids = (
            await self.db.scalars(select(Theme.id).where(Theme.name.in_(names)))
        ).all()
        await self.db.execute(
            delete(MediaLinkTheme).where(MediaLinkTheme.link_id == link_id)
        )
        await self.db.execute(
            insert(MediaLinkTheme).values(
                [{"link_id": link_id, "theme_id": t} for t in theme_ids]
            )
        )

    async def _reload(self, link_id: int) -> MediaLink:
        stmt = (
            select(MediaLink)
            .where(MediaLink.id == link_id)
            .execution_options(populate_existing=True)
        )
        return (await self.db.scalars(stmt)).one()
