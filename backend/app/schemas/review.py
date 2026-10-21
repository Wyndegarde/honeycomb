from pydantic import BaseModel, ConfigDict, Field


class NewReview(BaseModel):
    name: str = Field(max_length=2000)
    author: str = Field(max_length=2000)
    rating: int = Field(ge=0, le=5)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    author: str
    rating: int
