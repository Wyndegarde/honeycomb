from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_engine import get_session
from app.db.repositories.review import ReviewRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_review_repo() -> ReviewRepository:
    return ReviewRepository()


ReviewRepoDep = Annotated[ReviewRepository, Depends(get_review_repo)]
