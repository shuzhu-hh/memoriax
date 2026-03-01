from datetime import datetime

from pydantic import BaseModel, Field


class WordCreateRequest(BaseModel):
    word: str = Field(min_length=1, max_length=255)
    definition: str | None = None


class WordUpdateRequest(BaseModel):
    word: str = Field(min_length=1, max_length=255)
    definition: str | None = None


class WordResponse(BaseModel):
    id: int
    deck_id: int
    user_id: int
    word: str
    definition: str | None
    ease_factor: float
    interval: int
    repetition: int
    due_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WordListResponse(BaseModel):
    items: list[WordResponse]
    page: int
    size: int
    total: int


class WordImportRequest(BaseModel):
    content: str = Field(min_length=1)


class WordImportResponse(BaseModel):
    imported_count: int
    skipped_count: int = 0
