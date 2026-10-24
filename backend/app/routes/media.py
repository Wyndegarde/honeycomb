from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.db.models import MediaType
from app.routes.deps import LinkRepoDep, MediaDep, MediaRepoDep, get_media_or_404
from app.schemas.media import MediaRead, NewMedia, UpdateMedia

router = APIRouter(prefix="/media", tags=["media"])


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
async def get_media(media: MediaDep):
    return media


@router.post("", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def add_media(new_media: NewMedia, repo: MediaRepoDep, link_repo: LinkRepoDep):
    for link in new_media.links:
        await get_media_or_404(repo, link.media_id)
    media = await repo.create(**new_media.model_dump(exclude={"links"}))
    try:
        for link in new_media.links:
            await link_repo.add_link(media.id, link.media_id, link.themes, link.note)
    except IntegrityError:
        # A target was deleted after the check above; nothing is committed
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found") from None
    await repo.db.commit()
    return media


@router.patch("/{media_id}", response_model=MediaRead)
async def update_media(media: MediaDep, changes: UpdateMedia, repo: MediaRepoDep):
    media = await repo.update(media, **changes.model_dump(exclude_unset=True))
    await repo.db.commit()
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: int, repo: MediaRepoDep):
    if not await repo.delete(media_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    await repo.db.commit()
