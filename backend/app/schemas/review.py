from datetime import datetime

from pydantic import BaseModel, Field


class ReviewQueueItem(BaseModel):
    word_id: int
    word: str
    definition: str | None
    due_at: datetime | None
    repetition: int
    interval: int
    ease_factor: float
    is_new: bool


class ReviewGradeRequest(BaseModel):
    grade: int = Field(ge=0, le=4)


class ReviewResultResponse(BaseModel):
    word_id: int
    repetition: int
    interval: int
    ease_factor: float
    due_at: datetime | None


class DailyDueStat(BaseModel):
    date: str
    due_count: int


class ReviewStatsResponse(BaseModel):
    today_due_count: int
    total_due_count: int
    learned_count: int
    new_count: int
    next_7_days_due: list[DailyDueStat]

