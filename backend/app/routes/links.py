from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.db.models import MediaLink
from app.routes.deps import (
    LinkRepoDep,
    MediaRepoDep,
    get_link_or_404,
    get_media_or_404,
)
from app.schemas.link import LinkRead, NewLink, UpdateLink

router = APIRouter(prefix="/media/{media_id}/links", tags=["links"])


def to_read(link: MediaLink, media_id: int) -> LinkRead:
    other = link.target if link.source_id == media_id else link.source
    return LinkRead(
        media_id=other.id,
        title=other.title,
        themes=[t.name for t in link.themes],
        note=link.note,
    )


@router.get("", response_model=list[LinkRead])
async def list_links(
    media_id: int,
    repo: LinkRepoDep,
    media_repo: MediaRepoDep,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    await get_media_or_404(media_repo, media_id)
    links = await repo.list_for(media_id, limit, offset)
    return [to_read(link, media_id) for link in links]


@router.post("", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def add_link(
    media_id: int, new_link: NewLink, repo: LinkRepoDep, media_repo: MediaRepoDep
):
    if new_link.media_id == media_id:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Cannot link a Media to itself"
        )
    await get_media_or_404(media_repo, media_id)
    await get_media_or_404(media_repo, new_link.media_id)
    try:
        link = await repo.add_link(
            media_id, new_link.media_id, new_link.themes, new_link.note
        )
    except IntegrityError:
        # A Media was deleted after the checks above
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found") from None
    if link is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Link already exists; PATCH it instead"
        )
    await repo.db.commit()
    return to_read(link, media_id)


@router.patch("/{other_id}", response_model=LinkRead)
async def update_link(
    media_id: int, other_id: int, changes: UpdateLink, repo: LinkRepoDep
):
    link = await get_link_or_404(repo, media_id, other_id)
    fields = changes.model_dump(exclude_unset=True)
    link = await repo.update_link(
        link, fields.get("themes"), fields.get("note"), "note" in fields
    )
    await repo.db.commit()
    return to_read(link, media_id)


@router.delete("/{other_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(media_id: int, other_id: int, repo: LinkRepoDep):
    link = await get_link_or_404(repo, media_id, other_id)
    await repo.delete(link.id)
    await repo.db.commit()
