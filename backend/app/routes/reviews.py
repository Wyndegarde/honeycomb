from fastapi import APIRouter, HTTPException, status

from app.routes.deps import ReviewRepoDep, SessionDep
from app.schemas.review import NewReview, ReviewRead

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewRead])
async def get_all_reviews(session: SessionDep, repo: ReviewRepoDep):
    return await repo.list_all(session)


@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(review_id: int, session: SessionDep, repo: ReviewRepoDep):
    review = await repo.get(session, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    return review


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def add_review(new_review: NewReview, session: SessionDep, repo: ReviewRepoDep):
    review = await repo.create(session, **new_review.model_dump())
    await session.commit()
    return review
