from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_engine import get_session
from app.db.repositories.media import MediaRepository
from app.db.repositories.review import ReviewRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_media_repo(db: SessionDep) -> MediaRepository:
    return MediaRepository(db)


MediaRepoDep = Annotated[MediaRepository, Depends(get_media_repo)]


def get_review_repo(db: SessionDep) -> ReviewRepository:
    return ReviewRepository(db)


ReviewRepoDep = Annotated[ReviewRepository, Depends(get_review_repo)]
