from fastapi import APIRouter, HTTPException, Query, status

from app.db.models import Media, MediaType
from app.routes.deps import MediaRepoDep
from app.schemas.media import MediaRead, NewMedia, UpdateMedia

router = APIRouter(prefix="/media", tags=["media"])


async def get_media_or_404(repo: MediaRepoDep, media_id: int) -> Media:
    media = await repo.get(media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    return media


@router.get("", response_model=list[MediaRead])
async def list_media(
    repo: MediaRepoDep,
    q: str | None = None,
    type: MediaType | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await repo.search(q, type, limit, offset)


@router.get("/{media_id}", response_model=MediaRead)
async def get_media(media_id: int, repo: MediaRepoDep):
    return await get_media_or_404(repo, media_id)


@router.post("", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def add_media(new_media: NewMedia, repo: MediaRepoDep):
    media = await repo.create(**new_media.model_dump())
    await repo.db.commit()
    return media


@router.patch("/{media_id}", response_model=MediaRead)
async def update_media(media_id: int, changes: UpdateMedia, repo: MediaRepoDep):
    media = await get_media_or_404(repo, media_id)
    media = await repo.update(media, **changes.model_dump(exclude_unset=True))
    await repo.db.commit()
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: int, repo: MediaRepoDep):
    if not await repo.delete(media_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    await repo.db.commit()
