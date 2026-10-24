from pydantic import BaseModel, ConfigDict

from app.db.models import MediaType


class GraphNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    creator: str
    media_type: MediaType
    year: int | None


class GraphEdge(BaseModel):
    source: int
    target: int
    themes: list[str]
    note: str | None


class GraphRead(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
