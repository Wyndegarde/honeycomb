from fastapi import APIRouter, HTTPException, status

from app.routes.deps import MediaRepoDep, ReviewRepoDep
from app.schemas.review import NewReview, ReviewRead

router = APIRouter(prefix="/media/{media_id}/review", tags=["reviews"])


@router.get("", response_model=ReviewRead)
async def get_review(media_id: int, repo: ReviewRepoDep):
    review = await repo.get_by_media_id(media_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    return review


@router.put("", response_model=ReviewRead)
async def put_review(
    media_id: int,
    new_review: NewReview,
    repo: ReviewRepoDep,
    media_repo: MediaRepoDep,
):
    media = await media_repo.get(media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    review = await repo.upsert(media_id, **new_review.model_dump())
    # Keep media.review in sync for anything reading the same session afterwards
    await repo.db.refresh(media, ["review"])
    await repo.db.commit()
    return review


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(media_id: int, repo: ReviewRepoDep):
    review = await repo.get_by_media_id(media_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    await repo.db.delete(review)
    await repo.db.commit()
