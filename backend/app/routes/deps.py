from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_engine import get_session
from app.db.models import Media, MediaLink
from app.db.repositories.base import AsyncBaseRepository
from app.db.repositories.link import LinkRepository
from app.db.repositories.media import MediaRepository
from app.db.repositories.review import ReviewRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def repo_factory[R: AsyncBaseRepository](repo_cls: Callable[[AsyncSession], R]):
    def factory(db: SessionDep) -> R:
        return repo_cls(db)

    return factory


MediaRepoDep = Annotated[MediaRepository, Depends(repo_factory(MediaRepository))]
ReviewRepoDep = Annotated[ReviewRepository, Depends(repo_factory(ReviewRepository))]
LinkRepoDep = Annotated[LinkRepository, Depends(repo_factory(LinkRepository))]


async def get_media_or_404(repo: MediaRepoDep, media_id: int) -> Media:
    media = await repo.get(media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    return media


async def get_link_or_404(repo: LinkRepoDep, media_id: int, other_id: int) -> MediaLink:
    link = await repo.get_between(media_id, other_id)
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")
    return link


MediaDep = Annotated[Media, Depends(get_media_or_404)]
LinkDep = Annotated[MediaLink, Depends(get_link_or_404)]
