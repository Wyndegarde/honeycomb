from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models import MediaType
from app.schemas.review import ReviewRead


class NewMedia(BaseModel):
    title: str = Field(min_length=1, max_length=2000)
    creator: str = Field(min_length=1, max_length=2000)
    media_type: MediaType
    year: int | None = Field(default=None, ge=0, le=3000)
    description: str | None = Field(default=None, max_length=50000)


class UpdateMedia(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=2000)
    creator: str | None = Field(default=None, min_length=1, max_length=2000)
    media_type: MediaType | None = None
    year: int | None = Field(default=None, ge=0, le=3000)
    description: str | None = Field(default=None, max_length=50000)

    @field_validator("title", "creator", "media_type")
    @classmethod
    def not_null(cls, value):
        # These columns are NOT NULL; only year and description may be cleared.
        if value is None:
            raise ValueError("cannot be null")
        return value


class MediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    creator: str
    media_type: MediaType
    year: int | None
    description: str | None
    review: ReviewRead | None
