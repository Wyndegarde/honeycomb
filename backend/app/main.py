from typing import Annotated

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ConfigDict

from app.db.db_engine import get_session
from app.db.repositories.review import ReviewRepository

app = FastAPI()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class NewReview(BaseModel):
    name: str = Field(max_length=2000)
    author: str = Field(max_length=2000)
    rating: int = Field(ge=0, le=5)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    author: str
    rating: int


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.get("/review")
async def get_all_reviews():
    return {"reviews": []}


@app.post("/review", response_model=ReviewRead)
async def add_review(new_review: NewReview, session: SessionDep):
    review_repo = ReviewRepository()
    review = await review_repo.create(session, **new_review.model_dump())
    await session.commit()
    return review
