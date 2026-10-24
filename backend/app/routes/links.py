from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.db.models import MediaLink
from app.routes.deps import (
    LinkDep,
    LinkRepoDep,
    MediaDep,
    MediaRepoDep,
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
    media: MediaDep,
    repo: LinkRepoDep,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    links = await repo.list_for(media.id, limit, offset)
    return [to_read(link, media.id) for link in links]


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
    media_id: int, link: LinkDep, changes: UpdateLink, repo: LinkRepoDep
):
    fields = changes.model_dump(exclude_unset=True)
    link = await repo.update_link(
        link, fields.get("themes"), fields.get("note"), "note" in fields
    )
    await repo.db.commit()
    return to_read(link, media_id)


@router.delete("/{other_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(link: LinkDep, repo: LinkRepoDep):
    await repo.delete(link.id)
    await repo.db.commit()
