from fastapi import APIRouter

from app.routes.deps import LinkRepoDep, MediaRepoDep
from app.schemas.graph import GraphEdge, GraphRead

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphRead)
async def get_graph(repo: MediaRepoDep, link_repo: LinkRepoDep):
    return GraphRead(
        nodes=await repo.list_all(),  # type: ignore[arg-type] # validated from ORM objects
        edges=[
            GraphEdge(
                source=link.source_id,
                target=link.target_id,
                themes=[t.name for t in link.themes],
                note=link.note,
            )
            for link in await link_repo.list_all()
        ],
    )
