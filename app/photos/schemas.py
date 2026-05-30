from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class PhotoSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)


class PhotoResult(BaseModel):
    query: str
    image_url: HttpUrl | None = None
    thumb_url: HttpUrl | None = None
    alt_text: str | None = None
    photographer_name: str | None = None
    photographer_url: HttpUrl | None = None
    unsplash_page_url: HttpUrl | None = None
    source: Literal["unsplash", "fallback"] = "fallback"


class PhotoSearchResponse(PhotoResult):
    pass
