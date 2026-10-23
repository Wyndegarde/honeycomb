from pydantic import BaseModel, ConfigDict, Field


class NewReview(BaseModel):
    rating: int = Field(ge=0, le=5)
    body: str | None = Field(default=None, max_length=50000)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    media_id: int
    rating: int
    body: str | None
