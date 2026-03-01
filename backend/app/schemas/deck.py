from datetime import datetime

from pydantic import BaseModel, Field


class DeckCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class DeckUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class DeckResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DeckListResponse(BaseModel):
    items: list[DeckResponse]
    page: int
    size: int
    total: int


class DeckStatsResponse(BaseModel):
    total_words: int
    total_reviews: int
    reviews_today: int
    due_count: int
