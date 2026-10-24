from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, field_validator


def _normalise(names: list[str]) -> list[str]:
    # Lower-cased so Theme names are unique regardless of case
    cleaned = list(dict.fromkeys(n.strip().lower() for n in names))
    if not all(cleaned):
        raise ValueError("theme names cannot be blank")
    return cleaned


ThemeNames = Annotated[
    list[Annotated[str, Field(max_length=200)]],
    Field(min_length=1, max_length=20),
    AfterValidator(_normalise),
]


class NewLink(BaseModel):
    media_id: int
    themes: ThemeNames
    note: str | None = Field(default=None, max_length=50000)


class UpdateLink(BaseModel):
    themes: ThemeNames | None = None
    note: str | None = Field(default=None, max_length=50000)

    @field_validator("themes")
    @classmethod
    def not_null(cls, value):
        # A Link always needs at least one Connecting Theme; only note may be cleared.
        if value is None:
            raise ValueError("cannot be null")
        return value


class LinkRead(BaseModel):
    """A Link seen from one end: media_id/title describe the other Media."""

    media_id: int
    title: str
    themes: list[str]
    note: str | None
